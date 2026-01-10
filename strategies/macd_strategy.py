"""MACD策略"""

import hikyuu as hku


class MACDStrategy:
    """MACD策略
    
    使用MACD指标的金叉死叉来产生交易信号
    MACD线上穿信号线（金叉）时买入，下穿（死叉）时卖出
    """
    
    def __init__(self, fast_period=12, slow_period=26, signal_period=9, fixed_count=1000):
        """初始化MACD策略
        
        Args:
            fast_period: 快线周期，默认12日
            slow_period: 慢线周期，默认26日
            signal_period: 信号线周期，默认9日
            fixed_count: 固定买入数量，默认1000股
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.fixed_count = fixed_count
    
    def create_signal(self, kdata):
        """创建交易信号
        
        Args:
            kdata: K线数据
            
        Returns:
            sg: 交易信号对象
        """
        # 创建MACD指标
        macd = hku.MACD(kdata.close, self.fast_period, self.slow_period, self.signal_period)
        
        # MACD由MACD线、信号线、柱状图组成
        # MACD结果顺序：get_result(0)=BAR(柱状图), get_result(1)=DIF(MACD线), get_result(2)=DEA(信号线)
        # 使用 SLICE 提取子指标（返回 Indicator 对象）
        # SLICE(data, start, end, result_index) - result_index指定提取哪个结果集
        macd_line = hku.SLICE(macd, 0, -1, 1)  # MACD线 (DIF) - result_index=1
        signal_line = hku.SLICE(macd, 0, -1, 2)  # 信号线 (DEA) - result_index=2
        
        # 使用 SG_Cross 创建交叉信号：macd_line上穿signal_line时买入
        sg = hku.SG_Cross(macd_line, signal_line)
        
        return sg
    
    def create_money_manager(self):
        """创建资金管理策略
        
        Returns:
            mm: 资金管理对象
        """
        # 创建资金管理策略（固定每次买入指定数量）
        mm = hku.MM_FixedCount(self.fixed_count)
        return mm
    
    def get_description(self):
        """获取策略描述"""
        return f"MACD策略 (快线{self.fast_period}日, 慢线{self.slow_period}日, 信号线{self.signal_period}日, 固定{self.fixed_count}股)"
