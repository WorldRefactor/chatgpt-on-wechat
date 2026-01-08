import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *
from .data_engine import DataEngine  # <--- 引入你刚才写的引擎！

@plugins.register(
    name="Quant",
    desire_priority=100,
    desc="基于AkShare的A股分析助手",
    version="1.0",
    author="YourName",
)
class StockAnalyst(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        # 初始化你的引擎
        self.engine = DataEngine()
        logger.info("[StockAnalyst] 插件已初始化")

    def on_handle_context(self, e_context: EventContext):
        content = e_context["context"].content.strip()

        # 1. 设定触发指令：比如 "$诊股 600519"
        if content.startswith("$诊股"):
            logger.info(f"[StockAnalyst] 收到指令: {content}")
            
            # 2. 解析股票代码
            # 用户可能会输入 "$诊股 600519" 或 "$诊股 茅台" (暂只支持代码)
            parts = content.split()
            if len(parts) < 2:
                self._reply_text(e_context, "请输入股票代码，例如：$诊股 600519")
                return

            stock_code = parts[1]

            # 3. 提示用户正在处理（可选，防止用户以为卡死了）
            # 注意：微信可能会限制连续回复，这里先直接去跑数据

            try:
                # === 核心调用：使用你的 data_engine ===
                df = self.engine.fetch_and_process(stock_code)
                
                if df is None or df.empty:
                    self._reply_text(e_context, f"未找到代码 {stock_code} 的数据，请检查是否正确。")
                    return

                # 获取那段准备喂给 LLM 的字符串
                data_summary = self.engine.get_llm_summary(df)

                # === 4. 构建 Prompt (Analyst 角色) ===
                # 这就是 FinRobot 的 Analyst 逻辑
                prompt = f"""
你是一位资深的A股量化分析师。请根据以下实时数据，为用户撰写一份简短的分析报告。

【标的数据】
{data_summary}

【分析要求】
1. **趋势判断**：结合MA5和价格位置，判断短期是上涨、下跌还是震荡。
2. **指标解读**：RSI ({df.iloc[-1]['rsi']}) 是否发出了超买或超卖信号？
3. **操作建议**：用客观、专业的语气给出下周的关注点（压力位/支撑位）。
4. **风险提示**：简要说明风险。
5. **格式要求**： 报告最后必须单独一行输出以下免责声明：“(注：以上内容仅供参考，不构成投资建议)
请直接输出分析报告，不要罗列数据。
"""
                
                # === 5. 偷梁换柱 ===
                # 把用户的 "$诊股 600519" 替换成上面这一大段 Prompt
                # 然后让它继续传递给 ChatGPT (EventAction.CONTINUE)
                e_context["context"].type = ContextType.TEXT
                e_context["context"].content = prompt
                e_context.action = EventAction.CONTINUE 
                
            except Exception as e:
                logger.exception("[StockAnalyst] on_handle_context 崩了（带堆栈）")
                self._reply_text(e_context, "数据获取失败，可能是接口超时，请稍后再试。")

    def _reply_text(self, e_context, text):
        """辅助函数：直接回复文本并结束事件"""
        reply = Reply(ReplyType.TEXT, text)
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS