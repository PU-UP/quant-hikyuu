import hikyuu as hku
from strategies import EMACrossStrategy
from strategies.macd_strategy import MACDStrategy
from backtest import BacktestEngine
from strategies.all_strategies import *


def get_backtest_results(engine, kdata):
    """提取回测结果数据"""
    if engine.tm is None:
        return None
    
    init_cash = engine.tm.init_cash
    current_cash = engine.tm.current_cash
    
    # 计算持仓市值
    current_value = 0.0
    position_list = engine.tm.get_position_list()
    if len(position_list) > 0:
        current_price = kdata[-1].close if len(kdata) > 0 else 0
        for pos in position_list:
            try:
                number = pos.number if hasattr(pos, 'number') else 0
                current_value += number * current_price
            except:
                pass
    
    total_asset = current_cash + current_value
    total_return = total_asset - init_cash
    return_rate = (total_return / init_cash * 100) if init_cash > 0 else 0
    
    # 获取交易次数
    trade_list = []
    try:
        trade_list = engine.tm.get_trade_list()
        actual_trades = [t for t in trade_list if hasattr(t, 'business') and t.business.name != 'INIT']
        trade_count = len(actual_trades)
    except:
        trade_count = 0
    
    return {
        'init_cash': init_cash,
        'total_asset': total_asset,
        'total_return': total_return,
        'return_rate': return_rate,
        'trade_count': trade_count,
        'current_cash': current_cash,
        'current_value': current_value
    }


def run_strategy_backtest(strategy, kdata, init_cash=300000, verbose=False):
    """运行单个策略的回测"""
    if verbose:
        print(f"\n{'='*60}")
        print(f"测试策略: {strategy.get_description()}")
        print(f"{'='*60}")
    
    # 创建交易信号和资金管理
    sg = strategy.create_signal(kdata)
    mm = strategy.create_money_manager()
    
    # 创建回测引擎
    engine = BacktestEngine(init_cash=init_cash)
    engine.create_trade_account()
    engine.create_trade_system(sg, mm)
    
    # 运行回测
    if verbose:
        engine.run(kdata)
    else:
        engine.sys.run(kdata)
    
    # 获取结果
    results = get_backtest_results(engine, kdata)
    
    if verbose:
        engine.print_results(kdata)
    
    return results


def compare_strategies(strategies, kdata, init_cash=300000, verbose=False):
    """批量测试并对比多个策略"""
    results = []
    
    for strategy in strategies:
        try:
            result = run_strategy_backtest(strategy, kdata, init_cash, verbose)
            if result:
                result['strategy_name'] = strategy.get_description()
                results.append(result)
        except Exception as e:
            print(f"策略 {strategy.get_description()} 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    return results


def print_comparison_table(results):
    """打印策略对比表格"""
    if not results:
        print("没有可对比的结果")
        return
    
    print("\n" + "="*100)
    print("策略对比结果")
    print("="*100)
    print(f"{'策略名称':<40} {'初始资金':>12} {'总资产':>12} {'总收益':>12} {'收益率':>10} {'交易次数':>8}")
    print("-"*100)
    
    for r in results:
        print(f"{r['strategy_name']:<40} "
              f"{r['init_cash']:>12,.2f} "
              f"{r['total_asset']:>12,.2f} "
              f"{r['total_return']:>+12,.2f} "
              f"{r['return_rate']:>+9.2f}% "
              f"{r['trade_count']:>8}")
    
    print("-"*100)
    
    # 找出最佳策略
    if len(results) > 1:
        best_by_return = max(results, key=lambda x: x['total_return'])
        best_by_rate = max(results, key=lambda x: x['return_rate'])
        
        print(f"\n最佳总收益策略: {best_by_return['strategy_name']}")
        print(f"  总收益: {best_by_return['total_return']:,.2f} 元, "
              f"收益率: {best_by_return['return_rate']:.2f}%")
        
        if best_by_return != best_by_rate:
            print(f"\n最佳收益率策略: {best_by_rate['strategy_name']}")
            print(f"  总收益: {best_by_rate['total_return']:,.2f} 元, "
                  f"收益率: {best_by_rate['return_rate']:.2f}%")
    
    print("="*100 + "\n")


# ==================== 主程序 ====================

# 加载数据
print("加载数据...")
hku.load_hikyuu()
print("✓ 数据加载完成\n")

# 获取股票
# stock = hku.get_stock('sz000001')  # 平安银行
stock = hku.get_stock('sz002415')  # 海康威视
print(f"股票: {stock.market_code} - {stock.name}")

# 获取K线数据
kdata = stock.get_kdata(hku.Query(-150))  # 获取最近150条K线
print(f"K线数据: {len(kdata)} 条\n")

# 定义所有要测试的策略
strategies = [
    # EMACrossStrategy(fast_period=5, slow_period=10, fixed_count=1000),
    # MACDStrategy(fast_period=12, slow_period=26, signal_period=9, fixed_count=1000),
    # BollingerBreakoutStrategy(n=20, k=2, fixed_count=1000*2),
    EMACrossWithADXFilterStrategy(fast_period=5, slow_period=10, adx_period=14, adx_threshold=25, fixed_count=1000),
]

print(f"准备测试 {len(strategies)} 种策略...")
print("="*60)

# 批量测试所有策略（verbose=False 表示不输出详细过程）
results = compare_strategies(strategies, kdata, init_cash=300000, verbose=False)

# 打印对比表格
print_comparison_table(results)

# 如果需要查看某个策略的详细结果，可以单独运行：
# print("\n查看详细结果（EMA交叉策略）:")
# run_strategy_backtest(strategies[0], kdata, init_cash=300000, verbose=True)
