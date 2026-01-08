import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time
from common.log import logger
RENAME_MAP = {
    "日期": "date",
    "开盘": "open",
    "收盘": "close",
    "最高": "high",
    "最低": "low",
    "成交量": "volume",
    "涨跌幅": "pct_change"
}
KEEP_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume', 'pct_change', 'ma5', 'rsi']
class DataEngine:
    def __init__(self):
        pass

    def fetch_and_process(self, symbol="600519", period_days=60):
        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=period_days)).strftime("%Y%m%d")

            df = ak.stock_zh_a_hist(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
            )

            # ✅ 立刻把类型和列打出来（定位 akshare 返回了什么）
            logger.info(f"[DataEngine] type(df)={type(df)}")
            if df is None:
                logger.warning("[DataEngine] ak 返回 None")
                return pd.DataFrame()

            if not isinstance(df, pd.DataFrame):
                logger.warning(f"[DataEngine] ak 返回非 DataFrame: {type(df)} -> {df}")
                return pd.DataFrame()

            if df.empty:
                logger.warning("[DataEngine] ak 返回空 DataFrame")
                return pd.DataFrame()

            logger.info(f"[DataEngine] columns={list(df.columns)}")

            df = df.rename(columns=RENAME_MAP)

            # ✅ 重要：先排序再算 rolling（逻辑更对，也避免奇怪边界）
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df = df.sort_values("date")

            # ✅ 列存在性检查（避免后面 KeyError）
            required = ["close", "date"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                logger.warning(f"[DataEngine] 缺少关键列: {missing}")
                return pd.DataFrame()

            df["ma5"] = df["close"].rolling(window=5).mean()

            delta = df["close"].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)

            ma_up = up.ewm(com=13, adjust=False).mean()
            ma_down = down.ewm(com=13, adjust=False).mean()
            df["rsi"] = 100 - (100 / (1 + ma_up / ma_down))

            # ✅ KEEP_COLUMNS 缺啥就补啥，别让切片炸
            for c in KEEP_COLUMNS:
                if c not in df.columns:
                    df[c] = pd.NA

            final_df = df[KEEP_COLUMNS].copy()

            final_df["close"] = final_df["close"].round(2)
            final_df["rsi"] = final_df["rsi"].round(1)
            final_df["ma5"] = final_df["ma5"].round(2)

            return final_df

        except Exception:
            logger.exception("[DataEngine] fetch_and_process 崩了（带堆栈）")
            return pd.DataFrame()
    def get_llm_summary(self, df):
        if df is None or df.empty:
           return "无数据"
        latest = df.iloc[-1]
        history_str = df.tail(5).to_string(index = False)
        summary = (
            f"最新数据: {latest['date'].strftime('%Y-%m-%d')}\n"
            f"最新收盘价: {latest['close']}, ma5: {latest['ma5']}\n"
            f"RSI: {latest['rsi']} ({'超买' if latest['rsi'] > 70 else '超卖' if latest['rsi'] < 30 else '中性'}\n)"
            f"最近五日走势 {history_str}\n"
        )
        return summary
if __name__ == "__main__":
    engine = DataEngine()
    # 试试茅台
    data = engine.fetch_and_process("600519")
    
    print("\n✅ 数据处理完成，DataFrame 预览:")
    print(data.tail())
    
    print("\n✅ 准备喂给 LLM 的最终 Prompt 素材:")
    print("-" * 30)
    print(engine.get_llm_summary(data))
    print("-" * 30)
