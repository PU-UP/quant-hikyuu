"""EMA交叉策略"""

import hikyuu as hku


class EMACrossStrategy:
    """EMA交叉策略
    
    使用快线（5日EMA）和慢线（10日EMA）的交叉来产生交易信号
    快线上穿慢线时买入，下穿时卖出
    """
    
    def __init__(self, fast_period=5, slow_period=10, fixed_count=1000):
        """初始化EMA交叉策略
        
        Args:
            fast_period: 快线周期，默认5日
            slow_period: 慢线周期，默认10日
            fixed_count: 固定买入数量，默认1000股
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.fixed_count = fixed_count
    
    def create_signal(self, kdata):
        """创建交易信号
        
        Args:
            kdata: K线数据
            
        Returns:
            sg: 交易信号对象
        """
        # 创建技术指标
        ema_fast = hku.EMA(kdata.close, self.fast_period)
        ema_slow = hku.EMA(kdata.close, self.slow_period)
        
        # 创建交易信号（快线上穿慢线时买入，下穿时卖出）
        sg = hku.SG_Flex(ema_fast, slow_n=self.slow_period)
        
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
        return f"EMA交叉策略 (快线{self.fast_period}日, 慢线{self.slow_period}日, 固定{self.fixed_count}股)"
