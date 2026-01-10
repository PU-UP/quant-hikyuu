import hikyuu as hku

class BollingerBreakoutStrategy:
    """布林带突破：突破上轨买入，跌破中轨卖出"""
    def __init__(self, n=20, k=2, fixed_count=1000):
        self.n = n
        self.k = k
        self.fixed_count = fixed_count

    def create_signal(self, kdata):
        # 手动计算布林带，确保指标大小匹配
        close_price = kdata.close
        
        # 计算中轨（移动平均线）
        mid = hku.MA(close_price, self.n)
        
        # 计算标准差
        std = hku.STD(close_price, self.n)
        
        # 计算上轨和下轨，使用 hikyuu 的指标运算函数
        # 上轨 = 中轨 + k倍标准差
        k_val = hku.CVAL(self.k)  # 创建常数指标
        std_mult = hku.TA_MULT(std, k_val)  # std * k
        upper = hku.TA_ADD(mid, std_mult)    # mid + std*k
        
        # 创建价格上穿上轨的买入信号和下穿中轨的卖出信号
        buy_signal = hku.SG_Cross(close_price, upper)  # 价格上穿上轨
        sell_signal = hku.SG_Cross(mid, close_price)   # 中轨上穿价格（即价格下穿中轨）
        
        # 组合信号：使用 SG_Sub 组合，alternate=False 表示不交替
        sg = hku.SG_Sub(buy_signal, sell_signal, alternate=False)
        return sg

    def create_money_manager(self):
        return hku.MM_FixedCount(self.fixed_count)

    def get_description(self):
        return f"布林带突破 (n={self.n}, k={self.k}, fixed={self.fixed_count})"

class EMACrossWithADXFilterStrategy:
    """EMA交叉 + ADX趋势过滤（减少震荡区间的假信号）"""
    def __init__(self, fast_period=5, slow_period=10, adx_period=14, adx_threshold=25, fixed_count=1000):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold
        self.fixed_count = fixed_count

    def create_signal(self, kdata):
        ema_fast = hku.EMA(kdata.close, self.fast_period)
        ema_slow = hku.EMA(kdata.close, self.slow_period)

        # EMA交叉信号
        sg_cross = hku.SG_Flex(ema_fast, slow_n=self.slow_period)

        # 趋势强度（ADX）
        adx = hku.TA_ADX(kdata, self.adx_period)
        
        # ADX 返回的是包含 ADX、+DI、-DI 的复合指标
        # 提取 ADX 值（第一个结果集）
        adx_line = hku.SLICE(adx, 0, -1, 0)
        
        # 创建 ADX 过滤信号：当 ADX > threshold 时持续允许交易
        # 使用 SG_Band 创建基于条件的信号：当 adx_line 在 threshold 和 999 之间时买入
        # SG_Band(indicator, n1, n2) 当指标值在 n1 和 n2 之间时产生买入信号
        # 这样当 ADX > threshold 时会持续产生买入信号（允许交易）
        adx_filter = hku.SG_Band(adx_line, self.adx_threshold, 999.0)
        
        # 使用 SG_And 组合：EMA交叉信号 AND ADX过滤条件
        # SG_And 的逻辑：只有当两个信号都产生买入信号时，才买入
        # 只有当两个信号都产生卖出信号时，才卖出
        # 这意味着：只有当 ADX > threshold 且 EMA 交叉时，才产生交易信号
        sg = hku.SG_And(sg_cross, adx_filter, alternate=False)
        return sg

    def create_money_manager(self):
        return hku.MM_FixedCount(self.fixed_count)

    def get_description(self):
        return f"EMA交叉+ADX过滤 (fast={self.fast_period}, slow={self.slow_period}, ADX>{self.adx_threshold})"
