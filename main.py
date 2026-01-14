# main.py
# -*- coding: utf-8 -*-
"""
命令行入口：投资组合分析与再平衡建议
"""

from __future__ import annotations

# ============================================================
# 导入配置和模块
# ============================================================
from config import POSITIONS, CASH, TARGETS, RULES, INCLUDE_OTHER_FUNDS
from portfolio_module import (
    build_positions,
    portfolio_summary,
    rebalance_plan,
    positions_report,
)
from display_module import print_table, money, pct


# ============================================================
# 主程序（命令行版本）
# ============================================================

def main() -> None:
    positions = build_positions(POSITIONS)
    summary = portfolio_summary(positions, CASH, INCLUDE_OTHER_FUNDS)

    # -------- 痛点1：更真实的收益（至少把未实现/成本口径说清楚）--------
    print_table(
        ["指标", "数值"],
        [
            ["股票市值（现价）", money(summary["stock_market_value"])],
            ["股票成本总额", money(summary["stock_cost_value"])],
            ["未实现盈亏（持仓）", money(summary["unrealized_pnl"])],
            ["未实现收益率（按成本）", pct(summary["unrealized_pnl_pct_on_cost"])],
            ["证券账户现金", money(summary["stock_cash"])],
            ["其他资金计入投资池", money(summary["other_investable"]) if INCLUDE_OTHER_FUNDS else "不计入"],
            ["可投资总额（用于目标仓位计算）", money(summary["investable_total"])],
        ],
        title="组合总览（痛点1&4：收益口径 + 全资产可投资池）"
    )

    # 持仓明细（未实现盈亏贡献）
    positions_data = positions_report(positions)
    positions_rows = [
        [
            p["ticker"],
            p["group"],
            f"{p['shares']:g}",
            money(p["cost"]),
            money(p["price"]),
            money(p["cost_value"]),
            money(p["market_value"]),
            money(p["unrealized_pnl"]),
            pct(p["unrealized_pnl_pct"]),
        ]
        for p in positions_data
    ]
    print_table(
        ["Ticker", "Group", "Shares", "Cost", "Price", "CostValue", "MktValue", "UnrlzdPnL", "PnL%"],
        positions_rows,
        title="持仓明细（未实现盈亏贡献排行）"
    )

    # -------- 痛点2&3：目标仓位偏离 + 最大可买入（反冲动）--------
    deviation_data, action_data = rebalance_plan(
        positions=positions,
        cash=CASH,
        targets=TARGETS,
        include_other=INCLUDE_OTHER_FUNDS,
        rules=RULES,
    )

    # 转换为命令行显示格式
    deviation_rows = [
        [
            d["group"],
            money(d["current_value"]),
            pct(d["current_weight"]),
            pct(d["target_weight"]),
            money(d["target_value"]),
            money(d["diff"]),
            f"{d['diff_pct_point']*100:+.2f}pp",
            ("触发" if d["triggered"] else "未触发"),
        ]
        for d in deviation_data
    ]
    
    action_rows = [
        [
            a["group"],
            a["action"],
            money(a["action_amount"]),
            money(a["max_buy"]),
            money(a["max_trade_cash"]),
            money(a["stock_cash"]),
            ("是" if a["triggered"] else "否"),
        ]
        for a in action_data
    ]

    print_table(
        ["Group", "当前市值", "当前占比", "目标占比", "目标金额", "差额(目标-当前)", "权重差", "带宽触发"],
        deviation_rows,
        title="目标仓位偏离（痛点2：我到底超了/欠了多少？）"
    )

    print_table(
        ["Group", "建议", "建议调整金额", "最大可买入(纪律)", "单次现金上限", "当前现金", "触发再平衡?"],
        action_rows,
        title="执行建议（痛点3：给你\"最大可买入金额\"来刹冲动）"
    )

    # -------- 下一阶段预留：实现盈亏（痛点1 完整版）--------
    print("\n（预留）实现盈亏：下一阶段只要你加一张 TRADES（买卖记录），就能把已卖出也纳入总收益口径。")


if __name__ == "__main__":
    main()
