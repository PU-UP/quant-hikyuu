import hikyuu as hku

print("=" * 60)
print("步骤 1: hikyuu 已自动初始化")
print("=" * 60)
print(f"hikyuu 版本: {hku.__version__}")

# 1. 检查数据源配置
print("\n步骤 2: 检查数据源配置...")
try:
    # 检查 BASE_DIR（数据基础目录）
    if hasattr(hku, 'BASE_DIR'):
        print(f"数据基础目录 (BASE_DIR): {hku.BASE_DIR}")
    
    # 检查是否有 hub（数据仓库）
    hub_list = hku.get_hub_name_list()
    print(f"可用的数据仓库 (hub): {hub_list}")
    if len(hub_list) > 0:
        # get_current_hub 需要传入 hub 名称
        try:
            current_hub = hku.get_current_hub(hub_list[0])
            print(f"当前使用的 hub: {current_hub}")
        except:
            print(f"当前使用的 hub: {hub_list[0]}")
        # 尝试获取 hub 路径
        try:
            hub_path = hku.get_hub_path(hub_list[0])
            print(f"Hub 路径: {hub_path}")
        except:
            pass
    else:
        print("⚠ 未找到数据仓库，需要先配置数据源")
        print("  提示：可以使用 hku.add_local_hub() 添加本地数据仓库")
except Exception as e:
    print(f"检查数据源配置失败: {e}")
    import traceback
    traceback.print_exc()

# 2. 尝试加载 hikyuu 数据（如果存在）
print("\n步骤 3: 尝试加载 hikyuu 数据...")
try:
    # load_hikyuu 函数用于加载数据
    if hasattr(hku, 'load_hikyuu'):
        print("找到 load_hikyuu 函数，尝试加载数据...")
        # 注意：load_hikyuu 可能需要参数，这里先尝试不传参数
        # 如果失败，可能需要指定数据路径
        hku.load_hikyuu()
        print("✓ 数据加载完成")
    else:
        print("未找到 load_hikyuu 函数")
except Exception as e:
    print(f"✗ 加载数据失败: {e}")
    print("  提示：可能需要先配置数据源或导入数据")

# 3. 检查 StockManager 是否可用
print("\n步骤 4: 检查 StockManager...")
print(f"StockManager 对象: {hku.sm}")
print(f"StockManager 类型: {type(hku.sm)}")

# 4. 尝试获取股票总数
try:
    stock_count = len(hku.sm)
    print(f"股票总数: {stock_count}")
    if stock_count == 0:
        print("⚠ 股票列表为空，需要先配置数据源并导入股票数据")
except Exception as e:
    print(f"获取股票总数失败: {e}")

# 5. 尝试获取股票对象 - 方法1: 使用 get_stock
print("\n步骤 5: 尝试使用 get_stock() 获取股票...")
try:
    stock_code = 'sz000001'
    print(f"尝试获取股票: {stock_code}")
    stock = hku.get_stock(stock_code)
    print(f"✓ 成功获取股票对象: {stock}")
    print(f"  股票名称: {stock.name if hasattr(stock, 'name') else 'N/A'}")
    print(f"  股票代码: {stock.market_code if hasattr(stock, 'market_code') else 'N/A'}")
except Exception as e:
    print(f"✗ get_stock() 失败: {e}")
    stock = None

# 6. 尝试获取股票对象 - 方法2: 使用 StockManager
print("\n步骤 6: 尝试使用 StockManager 获取股票...")
try:
    stock_code2 = 'sz000001'
    print(f"尝试获取股票: {stock_code2}")
    stock2 = hku.sm[stock_code2]
    print(f"✓ 成功通过 StockManager 获取: {stock2}")
    if stock is None:
        stock = stock2
except Exception as e:
    print(f"✗ StockManager 获取失败: {e}")

# 7. 列出一些可用的股票代码（如果 StockManager 可用）
print("\n步骤 7: 尝试列出部分股票代码...")
try:
    if len(hku.sm) > 0:
        print("前10个股票代码:")
        count = 0
        # 注意：迭代 hku.sm 返回的是 Stock 对象，不是字符串代码
        for stock_obj in hku.sm:
            if count < 10:
                stock_code_str = stock_obj.market_code if hasattr(stock_obj, 'market_code') else str(stock_obj)
                stock_name = stock_obj.name if hasattr(stock_obj, 'name') else 'N/A'
                print(f"  {stock_code_str}: {stock_name}")
                count += 1
            else:
                break
    else:
        print("股票列表为空，可能需要先配置数据源")
except Exception as e:
    print(f"列出股票代码失败: {e}")
    import traceback
    traceback.print_exc()

# 8. 如果成功获取股票，尝试获取K线数据
if stock is not None:
    print("\n步骤 8: 尝试获取K线数据...")
    try:
        query = hku.Query(-100)  # 获取最近100条K线
        print(f"查询对象: {query}")
        kdata = stock.get_kdata(query)
        print(f"✓ 成功获取K线数据")
        print(f"  K线数量: {len(kdata)}")
        if len(kdata) > 0:
            first_k = kdata[0]
            last_k = kdata[-1]
            print(f"  第一条K线:")
            print(f"    日期: {first_k.datetime if hasattr(first_k, 'datetime') else 'N/A'}")
            print(f"    开盘: {first_k.open if hasattr(first_k, 'open') else 'N/A'}")
            print(f"    收盘: {first_k.close if hasattr(first_k, 'close') else 'N/A'}")
            print(f"  最后一条K线:")
            print(f"    日期: {last_k.datetime if hasattr(last_k, 'datetime') else 'N/A'}")
            print(f"    开盘: {last_k.open if hasattr(last_k, 'open') else 'N/A'}")
            print(f"    收盘: {last_k.close if hasattr(last_k, 'close') else 'N/A'}")
    except Exception as e:
        print(f"✗ 获取K线数据失败: {e}")
        print(f"  错误详情: {type(e).__name__}")
        import traceback
        traceback.print_exc()
else:
    print("\n步骤 8: 跳过（未成功获取股票对象）")

print("\n" + "=" * 60)
print("调试信息输出完成")
print("=" * 60)

# 总结
print("\n✓ 总结:")
if stock is not None and len(hku.sm) > 0:
    print(f"  ✓ 数据加载成功，共有 {len(hku.sm)} 只股票")
    print(f"  ✓ 成功获取股票: {stock.market_code if hasattr(stock, 'market_code') else 'N/A'} - {stock.name if hasattr(stock, 'name') else 'N/A'}")
    print(f"  ✓ 成功获取K线数据，可以开始进行策略分析和回测")
    print("\n下一步可以：")
    print("  1. 创建技术指标（如 MA、EMA、MACD 等）")
    print("  2. 创建交易信号（如金叉、死叉等）")
    print("  3. 创建资金管理策略")
    print("  4. 运行回测分析")
else:
    print("  ⚠ 部分步骤未成功，请检查上述错误信息")

print("\n提示：如果无法获取股票，可能需要：")
print("1. 配置数据源（如 tushare、聚宽等）")
print("2. 导入股票数据到 hikyuu（使用数据导入工具）")
print("3. 检查股票代码格式是否正确（如 'sz000001' 或 'sh000001'）")
print("4. 确保数据源已连接并包含该股票的数据")
print("\n参考资源：")
print("- 官方文档: https://hikyuu.readthedocs.io/")
print("- GitHub: https://github.com/fasiondog/hikyuu")
print("- QQ交流群: 114910869")
