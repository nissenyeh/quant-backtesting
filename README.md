# Stock Backtesting

收集各種有趣的回測點子，用數據驗證投資理論與策略

---

## 回測項目

| 項目 | 關鍵問題 | 說明 |
|------|---------|------|
| [經濟週期報酬率回測](./period_return_backtest/) | 經濟衰退前的榮景期是否適合將持股降低為 0（以避免衰退期的風險）？榮景期最後幾年的報酬如何？ | 驗證「『經濟衰退前的榮景期』末期不應將持股完全降至 0」的論述是否合理（分析 1926-2022 年各經濟週期末 1-3 年的 S&P 500 報酬率） |
| [股市熊市（經濟衰退型熊市 vs 非經濟衰退型熊市）分析](./bear_market_analysis/) | 多數熊市會伴隨經濟衰退嗎？兩種熊市的下跌/恢復速度差異？是否能利用經濟指標判斷最佳買點？ | 回測經濟衰退型熊市 vs 非衰退型熊市的跌幅、恢復時間與最佳買點（分析 1970-2026 年 S&P 500 熊市） |




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


