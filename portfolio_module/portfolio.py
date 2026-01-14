# portfolio.py
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Position:
    ticker: str
    group: str
    shares: float
    cost: float
    price: float

    @property
    def market_value(self) -> float:
        return self.shares * self.price

    @property
    def cost_value(self) -> float:
        return self.shares * self.cost

    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.cost_value

    @property
    def unrealized_pnl_pct(self) -> float:
        base = self.cost_value
        return (self.unrealized_pnl / base) if base != 0 else 0.0


def build_positions(raw: List[Dict]) -> List[Position]:
    return [
        Position(
            ticker=str(p["ticker"]),
            group=str(p["group"]),
            shares=float(p["shares"]),
            cost=float(p["cost"]),
            price=float(p["price"]),
        )
        for p in raw
    ]


def portfolio_summary(positions: List[Position], cash: Dict, include_other: bool) -> Dict[str, float]:
    stock_mv = sum(p.market_value for p in positions)
    stock_cost = sum(p.cost_value for p in positions)
    unrealized = stock_mv - stock_cost

    stock_cash = float(cash.get("stock_cash", 0.0))
    other_investable = float(cash.get("other_funds_investable", 0.0)) if include_other else 0.0
    investable_total = stock_mv + stock_cash + other_investable

    return {
        "stock_market_value": stock_mv,
        "stock_cost_value": stock_cost,
        "unrealized_pnl": unrealized,
        "unrealized_pnl_pct_on_cost": (unrealized / stock_cost) if stock_cost else 0.0,
        "stock_cash": stock_cash,
        "other_investable": other_investable,
        "investable_total": investable_total,
    }


def group_current_values(positions: List[Position]) -> Dict[str, float]:
    g: Dict[str, float] = {}
    for p in positions:
        g[p.group] = g.get(p.group, 0.0) + p.market_value
    return g


def normalize_targets(targets: List[Dict]) -> Dict[str, Dict[str, float]]:
    t = {x["group"]: {"w": float(x["target_weight"]), "band": float(x.get("band", 0.0))} for x in targets}
    total_w = sum(v["w"] for v in t.values())
    if abs(total_w - 1.0) > 1e-6:
        # 容错：权重不为 1 时自动归一
        for k in t:
            t[k]["w"] = t[k]["w"] / total_w if total_w else 0.0
    return t


def rebalance_plan(
    positions: List[Position],
    cash: Dict,
    targets: List[Dict],
    include_other: bool,
    rules: Dict,
) -> Tuple[List[Dict], List[Dict]]:
    """
    返回两张表的数据（字典格式，便于显示）：
    1) 板块偏离表
    2) 执行建议表（买/卖候选、最大可买入金额、是否触发带宽）
    """
    summary = portfolio_summary(positions, cash, include_other)
    investable_total = summary["investable_total"]
    stock_cash = summary["stock_cash"]

    t = normalize_targets(targets)
    cur_by_group = group_current_values(positions)

    # 规则：单次最多动用现金的比例（反冲动）
    max_trade_cash = stock_cash * float(rules.get("max_trade_cash_fraction", 1.0))

    deviation_rows: List[Dict] = []
    action_rows: List[Dict] = []

    # 为了保证 targets 里没出现但 positions 里有的 group 也能显示
    all_groups = sorted(set(list(t.keys()) + list(cur_by_group.keys())))

    for g in all_groups:
        cur = cur_by_group.get(g, 0.0)
        w = t.get(g, {}).get("w", 0.0)
        band = t.get(g, {}).get("band", 0.0)

        target_value = investable_total * w
        diff = target_value - cur  # 正数=欠配（应该买），负数=超配（应该卖）

        # 带宽触发：相对目标金额偏离超过 band
        # 例如 band=0.1：偏离超过目标金额的10%才算触发
        trigger = False
        if target_value > 0:
            trigger = abs(diff) > (target_value * band)

        cur_w = (cur / investable_total) if investable_total else 0.0
        diff_pct_point = cur_w - w  # 当前权重-目标权重（百分点）

        deviation_rows.append({
            "group": g,
            "current_value": cur,
            "current_weight": cur_w,
            "target_weight": w,
            "target_value": target_value,
            "diff": diff,
            "diff_pct_point": diff_pct_point,
            "triggered": trigger,
        })

        # 最大可买入：不能超过欠配金额、不能超过现金、不能超过单次现金使用上限
        if diff > 0:
            max_buy = min(diff, stock_cash, max_trade_cash)
            action = "BUY"
            action_amount = max_buy
        elif diff < 0:
            # 卖出建议先只给"需要减少的金额"，具体卖哪只后续可扩展
            action = "SELL"
            action_amount = abs(diff)
            max_buy = 0.0
        else:
            action = "HOLD"
            action_amount = 0.0
            max_buy = 0.0

        action_rows.append({
            "group": g,
            "action": action,
            "action_amount": action_amount,
            "max_buy": max_buy,
            "max_trade_cash": max_trade_cash,
            "stock_cash": stock_cash,
            "triggered": trigger,
        })

    # 按绝对偏离排序
    deviation_rows_sorted = sorted(
        deviation_rows,
        key=lambda r: abs(r["diff"]),
        reverse=True
    )

    # 让行动表按：先触发、再欠配金额/超配金额排序
    action_rows_sorted = sorted(
        action_rows,
        key=lambda r: (-r["triggered"], -r["action_amount"])
    )

    return deviation_rows_sorted, action_rows_sorted


def positions_report(positions: List[Position]) -> List[Dict]:
    """返回持仓报告数据（字典格式）"""
    seen = set()
    result = []
    
    for p in positions:
        # 使用 ticker 作为唯一标识，防止重复
        if p.ticker in seen:
            continue
        seen.add(p.ticker)
        
        result.append({
            "ticker": p.ticker,
            "group": p.group,
            "shares": p.shares,
            "cost": p.cost,
            "price": p.price,
            "cost_value": p.cost_value,
            "market_value": p.market_value,
            "unrealized_pnl": p.unrealized_pnl,
            "unrealized_pnl_pct": p.unrealized_pnl_pct,
        })
    
    # 按未实现盈亏贡献排序（最影响你心态的先看）
    result.sort(key=lambda r: (r["unrealized_pnl"], r["ticker"]), reverse=True)
    return result
