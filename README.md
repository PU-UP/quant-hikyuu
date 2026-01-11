# Quant Hikyuu

基于 Hikyuu 框架的量化交易策略回测系统。

## 项目简介

本项目提供了一个完整的量化交易策略回测框架，支持多种技术指标策略的开发和测试，包括 EMA 交叉策略、MACD 策略等。

## 功能特性

- 📊 支持多种技术指标策略（EMA、MACD 等）
- 🔄 完整的回测引擎，支持策略性能评估
- 📈 策略对比功能，可批量测试多个策略
- 💰 灵活的资金管理配置
- 📉 详细的回测结果统计

## 环境要求

- Python 3.11 / 3.12（推荐）
- pip（最新版本）

## 安装步骤

### 1. 创建虚拟环境（推荐）

```bash
python -m venv .venv
```

### 2. 激活虚拟环境

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. 升级 pip

```bash
python -m pip install -U pip
```

### 4. 安装依赖

```bash
pip install hikyuu
```

## 数据配置

### 数据下载

本项目使用图达通（hikyuutdx）下载数据。

### 数据源配置

1. 配置数据源（如 tushare、聚宽等）
2. 导入股票数据到 hikyuu
3. 确保数据源已连接并包含所需股票数据

## 项目结构

```
quant-hikyuu/
├── backtest/              # 回测引擎模块
│   ├── __init__.py
│   └── engine.py         # 回测引擎实现
├── strategies/            # 策略模块
│   ├── __init__.py
│   ├── all_strategies.py # 所有策略汇总
│   ├── ema_cross_strategy.py  # EMA 交叉策略
│   └── macd_strategy.py       # MACD 策略
├── demo.py               # 基础示例
├── backtest_demo.py      # 回测示例
└── README.md
```

## 使用示例

### 基础使用

运行 `demo.py` 查看基础功能演示：

```bash
python demo.py
```

### 策略回测

运行 `backtest_demo.py` 进行策略回测：

```bash
python backtest_demo.py
```

## 推荐MCP

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "D:\\Applications\\node\\npx.cmd",
      "args": ["-y", "@modelcontextprotocol/server-filesystem@latest", "D:\\Projects\\github\\quant-hikyuu"]
    },
    "run_python": {
      "command": "C:\\Users\\WINDOWS\\.cursor\\run_mcp_python.bat"
    },
    "ripgrep": {
      "command": "D:\\Applications\\node\\npx.cmd",
      "args": ["-y", "mcp-ripgrep@latest"]
    }
  }
}
```

## 相关资源

- [Hikyuu 官方文档](https://hikyuu.readthedocs.io/)
- [Hikyuu GitHub](https://github.com/fasiondog/hikyuu)
- QQ 交流群: 114910869

## 许可证

本项目基于 Hikyuu 框架开发，请遵循相应的开源协议。
