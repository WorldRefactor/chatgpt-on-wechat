Quant (A股 AI 投研助手)

简介 / Introduction
Quant 是一款基于 `chatgpt-on-wechat` 的 A 股量化分析插件。

它利用 [AkShare](https://github.com/akfamily/akshare) 获取实时的 A 股行情数据（包括复权价格、成交量等），并结合 Pandas 进行清洗与计算技术指标（如 RSI, MA5）。最终，它将处理好的结构化数据投喂给 LLM，生成一份专业的、带有趋势预判的实时投研报告。

> 核心价值：告别冰冷的数据罗列，让 AI 像分析师一样告诉你“发生了什么”以及“该怎么办”。

✨ 功能特性 / Features
实时数据抓取：基于 AkShare 接口，秒级获取 A 股个股最新行情。
量化指标计算：
MA5：判断短期价格趋势。
RSI (14)：识别超买/超卖信号，辅助判断顶底。
前复权 (qfq)：确保 K 线分析的连续性与准确性。
AI 深度解读：自动生成包含趋势判断、操作建议和风险提示的分析报告。
极简设计：只依赖 Pandas 和 AkShare，无需配置 API Key，开箱即用。

安装与依赖 / Installation
本插件依赖以下 Python 库，插件加载时会自动安装（请确保目录下包含 `requirements.txt`）：

```bash
pip install akshare pandas
⚠️ 免责声明 / Disclaimer
本插件提供的所有数据与 AI 分析结果仅供参考，**不构成任何投资建议**。
股市有风险，入市需谨慎。开发者不对因使用本插件产生的任何盈亏负责。