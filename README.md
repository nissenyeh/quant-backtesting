# Stock Backtesting

收集各種有趣的回測點子，用數據驗證投資理論與策略

---

## 回測項目

| 項目 | 說明 | 
|------|------|
| [經濟週期報酬率回測](./period_return_backtest/) | 驗證「榮景期（泡沫）末期不應將持股完全降至逾 0」的論述，分析 1926-2022 年各經濟週期的 S&P 500 報酬率 | 



# 使用教學

1. Clone 或下載這個 repo：
```bash
git clone https://github.com/nissenyeh/quant-backtesting
cd stock-backtesting
```

2. 安裝 [Claude Code](https://docs.anthropic.com/en/docs/claude-code)：
```bash
npm install -g @anthropic-ai/claude-code
```

3. 進入想跑的回測資料夾，啟動 Claude Code：
```bash
cd period_return_backtest
claude
```

4. 輸入：
```
請讀取這個資料夾的 README，然後幫我跑回測
```

Claude Code 會自動讀取 README、安裝依賴、執行腳本並產出結果。


