# display.py
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict, List, Optional
import streamlit as st
import pandas as pd


def money(x: float) -> str:
    return f"¥{x:,.2f}"


def pct(x: float) -> str:
    return f"{x*100:,.2f}%"


# ============================================================
# 命令行显示函数
# ============================================================

def print_table(headers: List[str], rows: List[List[str]], title: Optional[str] = None) -> None:
    """命令行版本的表格打印"""
    if title:
        print("\n" + "=" * len(title))
        print(title)
        print("=" * len(title))

    # 简易对齐
    col_widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(r: List[str]) -> str:
        return " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(r))

    print(fmt_row(headers))
    print("-+-".join("-" * w for w in col_widths))
    for r in rows:
        print(fmt_row(r))


# ============================================================
# Streamlit 显示函数
# ============================================================

def display_portfolio_summary(summary: Dict[str, float], include_other: bool) -> None:
    """显示组合总览"""
    st.header("📊 组合总览")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("股票市值（现价）", money(summary["stock_market_value"]))
        st.metric("股票成本总额", money(summary["stock_cost_value"]))
    
    with col2:
        pnl = summary["unrealized_pnl"]
        pnl_pct = summary["unrealized_pnl_pct_on_cost"]
        st.metric(
            "未实现盈亏（持仓）",
            money(pnl),
            delta=f"{pnl_pct*100:+.2f}%"
        )
        st.metric("证券账户现金", money(summary["stock_cash"]))
    
    with col3:
        st.metric("其他资金计入投资池", money(summary["other_investable"]) if include_other else "不计入")
        st.metric("可投资总额", money(summary["investable_total"]))


def display_positions(positions_data: List[Dict]) -> None:
    """显示持仓明细"""
    st.header("📈 持仓明细（未实现盈亏贡献排行）")
    
    df = pd.DataFrame(positions_data)
    
    # 格式化显示
    display_df = pd.DataFrame({
        "股票代码": df["ticker"],
        "板块": df["group"],
        "股数": df["shares"].apply(lambda x: f"{x:g}"),
        "成本价": df["cost"].apply(money),
        "现价": df["price"].apply(money),
        "成本总额": df["cost_value"].apply(money),
        "市值": df["market_value"].apply(money),
        "未实现盈亏": df["unrealized_pnl"].apply(money),
        "盈亏%": df["unrealized_pnl_pct"].apply(pct),
    })
    
    # 添加颜色标记
    def color_pnl(val):
        if isinstance(val, str) and val.startswith("¥"):
            num = float(val.replace("¥", "").replace(",", ""))
            if num > 0:
                return 'background-color: #d4edda'  # 绿色
            elif num < 0:
                return 'background-color: #f8d7da'  # 红色
        return ''
    
    styled_df = display_df.style.applymap(color_pnl, subset=["未实现盈亏"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


def display_deviation(deviation_data: List[Dict]) -> None:
    """显示目标仓位偏离"""
    st.header("🎯 目标仓位偏离")
    
    df = pd.DataFrame(deviation_data)
    
    display_df = pd.DataFrame({
        "板块": df["group"],
        "当前市值": df["current_value"].apply(money),
        "当前占比": df["current_weight"].apply(pct),
        "目标占比": df["target_weight"].apply(pct),
        "目标金额": df["target_value"].apply(money),
        "差额": df["diff"].apply(money),
        "权重差": df["diff_pct_point"].apply(lambda x: f"{x*100:+.2f}pp"),
        "带宽触发": df["triggered"].apply(lambda x: "✅ 触发" if x else "⏸️ 未触发"),
    })
    
    # 添加颜色标记
    def color_diff(val):
        if isinstance(val, str) and val.startswith("¥"):
            num = float(val.replace("¥", "").replace(",", ""))
            if num > 0:
                return 'background-color: #fff3cd'  # 黄色（欠配）
            elif num < 0:
                return 'background-color: #d1ecf1'  # 蓝色（超配）
        return ''
    
    styled_df = display_df.style.applymap(color_diff, subset=["差额"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # 可视化：当前占比 vs 目标占比
    st.subheader("占比对比图")
    chart_df = pd.DataFrame({
        "板块": df["group"],
        "当前占比": df["current_weight"] * 100,
        "目标占比": df["target_weight"] * 100,
    })
    chart_df = chart_df.set_index("板块")
    st.bar_chart(chart_df)


def display_actions(action_data: List[Dict]) -> None:
    """显示执行建议"""
    st.header("💡 执行建议（反冲动纪律）")
    
    df = pd.DataFrame(action_data)
    
    display_df = pd.DataFrame({
        "板块": df["group"],
        "建议": df["action"].apply(lambda x: {
            "BUY": "🟢 买入",
            "SELL": "🔴 卖出",
            "HOLD": "⚪ 持有"
        }.get(x, x)),
        "建议调整金额": df["action_amount"].apply(money),
        "最大可买入(纪律)": df["max_buy"].apply(money),
        "单次现金上限": df["max_trade_cash"].apply(money),
        "当前现金": df["stock_cash"].apply(money),
        "触发再平衡": df["triggered"].apply(lambda x: "✅ 是" if x else "❌ 否"),
    })
    
    # 高亮触发再平衡的行
    def highlight_triggered(row):
        if row["触发再平衡"] == "✅ 是":
            return ['background-color: #fff3cd'] * len(row)
        return [''] * len(row)
    
    styled_df = display_df.style.apply(highlight_triggered, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # 显示关键信息
    triggered_groups = df[df["triggered"] == True]
    if len(triggered_groups) > 0:
        st.info(f"⚠️ 有 {len(triggered_groups)} 个板块触发了再平衡条件")
        
        buy_groups = triggered_groups[triggered_groups["action"] == "BUY"]
        sell_groups = triggered_groups[triggered_groups["action"] == "SELL"]
        
        if len(buy_groups) > 0:
            st.success(f"🟢 建议买入板块：{', '.join(buy_groups['group'].tolist())}")
        if len(sell_groups) > 0:
            st.warning(f"🔴 建议卖出板块：{', '.join(sell_groups['group'].tolist())}")


def display_all(
    summary: Dict[str, float],
    positions_data: List[Dict],
    deviation_data: List[Dict],
    action_data: List[Dict],
    include_other: bool,
) -> None:
    """显示所有信息"""
    display_portfolio_summary(summary, include_other)
    st.divider()
    display_positions(positions_data)
    st.divider()
    display_deviation(deviation_data)
    st.divider()
    display_actions(action_data)
