"""回测引擎"""

import hikyuu as hku


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, init_cash=300000):
        """初始化回测引擎
        
        Args:
            init_cash: 初始资金，默认30万
        """
        self.init_cash = init_cash
        self.tm = None
        self.sys = None
    
    def create_trade_account(self):
        """创建交易账户"""
        self.tm = hku.crtTM(init_cash=self.init_cash)
        return self.tm
    
    def create_trade_system(self, sg, mm):
        """创建交易系统
        
        Args:
            sg: 交易信号
            mm: 资金管理策略
            
        Returns:
            sys: 交易系统对象
        """
        if self.tm is None:
            self.create_trade_account()
        
        self.sys = hku.SYS_Simple(tm=self.tm, sg=sg, mm=mm)
        return self.sys
    
    def run(self, kdata):
        """运行回测
        
        Args:
            kdata: K线数据
        """
        if self.sys is None:
            raise ValueError("交易系统未创建，请先调用 create_trade_system")
        
        print("=" * 60)
        print("开始回测...")
        self.sys.run(kdata)
        print("=" * 60)
    
    def print_results(self, kdata):
        """输出回测结果
        
        Args:
            kdata: K线数据
        """
        if self.tm is None:
            raise ValueError("交易账户未创建")
        
        print("\n回测结果:")
        print("-" * 60)
        init_cash = self.tm.init_cash
        current_cash = self.tm.current_cash
        
        # 计算持仓市值（通过持仓记录和当前价格）
        current_value = 0.0
        position_list = self.tm.get_position_list()
        if len(position_list) > 0:
            # 获取最后一条K线的收盘价作为当前价格
            current_price = kdata[-1].close if len(kdata) > 0 else 0
            for pos in position_list:
                try:
                    number = pos.number if hasattr(pos, 'number') else 0
                    current_value += number * current_price
                except:
                    pass
        
        total_asset = current_cash + current_value
        
        print(f"初始资金:     {init_cash:>12,.2f} 元")
        print(f"当前现金:     {current_cash:>12,.2f} 元")
        print(f"持仓市值:     {current_value:>12,.2f} 元")
        print(f"总资产:       {total_asset:>12,.2f} 元")
        print("-" * 60)
        
        total_return = total_asset - init_cash
        return_rate = (total_return / init_cash * 100) if init_cash > 0 else 0
        print(f"总收益:       {total_return:>12,.2f} 元")
        print(f"收益率:       {return_rate:>11.2f}%\n")
        
        # 获取交易记录
        self._print_trade_list()
        
        # 获取持仓记录
        self._print_position_list(kdata)
        
        print("\n" + "=" * 60)
        print("回测完成！")
        print("=" * 60)
    
    def _print_trade_list(self):
        """打印交易记录"""
        trade_list = []
        try:
            trade_list = self.tm.get_trade_list()
            # 过滤掉 INIT 类型的交易
            actual_trades = [t for t in trade_list if hasattr(t, 'business') and t.business.name != 'INIT']
            print(f"交易次数: {len(actual_trades)} 次（不含初始化）")
            
            if len(actual_trades) > 0:
                print("\n交易记录（前10笔）:")
                print("-" * 60)
                print(f"{'序号':<4} {'日期':<12} {'类型':<6} {'价格':>8} {'数量':>8} {'金额':>12}")
                print("-" * 60)
                for i, trade in enumerate(actual_trades[:10]):
                    try:
                        dt = str(trade.datetime)[:10] if hasattr(trade, 'datetime') else 'N/A'
                        business = trade.business.name if hasattr(trade, 'business') else 'N/A'
                        number = trade.number if hasattr(trade, 'number') else 0
                        
                        # 使用正确的属性名：real_price (不是 realPrice)
                        price = trade.real_price if hasattr(trade, 'real_price') else (trade.plan_price if hasattr(trade, 'plan_price') else 0)
                        amount = number * price
                        print(f"{i+1:<4} {dt:<12} {business:<6} {price:>8.2f} {number:>8.0f} {amount:>12.2f}")
                    except Exception as e:
                        print(f"{i+1:2d}. 解析失败: {e}")
                        print(f"    Trade对象: {trade}")
        except Exception as e:
            print(f"获取交易记录失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _print_position_list(self, kdata):
        """打印持仓记录
        
        Args:
            kdata: K线数据
        """
        try:
            position_list = self.tm.get_position_list()
            trade_list = self.tm.get_trade_list()
            
            if len(position_list) > 0:
                current_price = kdata[-1].close if len(kdata) > 0 else 0
                print(f"\n当前持仓: {len(position_list)} 只")
                print("-" * 60)
                print(f"{'代码':<12} {'数量':>8} {'成本价':>10} {'当前价':>10} {'市值':>12} {'盈亏':>12} {'盈亏率':>8}")
                print("-" * 60)
                for pos in position_list:
                    try:
                        code = pos.stock.market_code if hasattr(pos, 'stock') else 'N/A'
                        number = pos.number if hasattr(pos, 'number') else 0
                        
                        # 尝试多种方式获取买入金额
                        buy_money = 0
                        if hasattr(pos, 'buyMoney'):
                            buy_money = pos.buyMoney
                        elif hasattr(pos, 'total_cost'):
                            buy_money = pos.total_cost
                        elif hasattr(pos, 'cost'):
                            buy_money = pos.cost
                        else:
                            # 如果没有buyMoney，尝试从交易记录中计算
                            # 找到该股票的所有买入交易
                            buy_trades = [t for t in trade_list 
                                         if hasattr(t, 'stock') and hasattr(t.stock, 'market_code') 
                                         and t.stock.market_code == code 
                                         and hasattr(t, 'business') and t.business.name == 'BUY']
                            if buy_trades:
                                buy_money = sum(t.number * (t.real_price if hasattr(t, 'real_price') else t.plan_price) 
                                               for t in buy_trades if hasattr(t, 'number'))
                        
                        cost = (buy_money / number) if number > 0 else 0
                        market_value = number * current_price
                        profit = market_value - buy_money
                        profit_rate = (profit / buy_money * 100) if buy_money > 0 else 0
                        
                        print(f"{code:<12} {number:>8.0f} {cost:>10.2f} {current_price:>10.2f} {market_value:>12.2f} {profit:>+12.2f} {profit_rate:>+7.2f}%")
                    except Exception as e:
                        print(f"解析持仓失败: {e}")
                        # 打印持仓对象的所有属性以便调试
                        print(f"  持仓对象属性: {dir(pos)}")
                        print(f"  持仓对象: {pos}")
            else:
                print("\n当前无持仓")
        except Exception as e:
            print(f"\n获取持仓记录失败: {e}")
            import traceback
            traceback.print_exc()
