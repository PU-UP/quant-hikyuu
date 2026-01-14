# app.py
# -*- coding: utf-8 -*-

import streamlit as st
from portfolio_module import (
    build_positions,
    portfolio_summary,
    rebalance_plan,
    positions_report,
)
from display_module import display_all
from config import POSITIONS, CASH, TARGETS, RULES, INCLUDE_OTHER_FUNDS

st.set_page_config(
    page_title="投资组合分析",
    page_icon="📊",
    layout="wide",
)

st.title("📊 投资组合分析与再平衡建议")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")
    st.info("当前使用配置文件中的数据")
    st.caption("如需修改，请编辑 main.py 中的配置")

# 计算数据
positions = build_positions(POSITIONS)
summary = portfolio_summary(positions, CASH, INCLUDE_OTHER_FUNDS)
positions_data = positions_report(positions)
deviation_data, action_data = rebalance_plan(
    positions=positions,
    cash=CASH,
    targets=TARGETS,
    include_other=INCLUDE_OTHER_FUNDS,
    rules=RULES,
)

# 显示所有信息
display_all(
    summary=summary,
    positions_data=positions_data,
    deviation_data=deviation_data,
    action_data=action_data,
    include_other=INCLUDE_OTHER_FUNDS,
)

# 页脚
st.divider()
st.caption("💡 提示：未实现盈亏 = 当前市值 - 成本总额，卖出前只是账面盈亏")
