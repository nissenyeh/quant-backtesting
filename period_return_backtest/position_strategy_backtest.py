#!/usr/bin/env python3
"""
持股水位策略回測

研究問題：
1. 用精確時間區段（衰退前12個月、24個月、36個月）計算報酬
2. 回測不同持股水位策略的表現

策略：
- A: 100% 持股（不調整）
- B: 擴張期最後1年降到 50%
- C: 擴張期最後1年清倉 0%
"""

import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 取得腳本所在目錄
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 讀取 Shiller 月數據
sp_data = pd.read_csv(os.path.join(SCRIPT_DIR, 'input_SP指數(Shiller數據）.csv'))
sp_data['Year'] = sp_data['Date 日期(年.月)'].apply(lambda x: int(str(x).split('.')[0]))
sp_data['Month'] = sp_data['Date 日期(年.月)'].apply(lambda x: int(str(x).split('.')[1]) if '.' in str(x) else 1)
sp_data['Total_Return_Index'] = sp_data['Real Total Return Price 通膨調整+股息再投入指數'].astype(str).str.replace(',', '').astype(float)
sp_data['Date'] = pd.to_datetime(sp_data['Year'].astype(str) + '-' + sp_data['Month'].astype(str).str.zfill(2) + '-01')
sp_data = sp_data.sort_values('Date').reset_index(drop=True)

def get_index_at_date(year, month):
    """取得某年月的指數值"""
    row = sp_data[(sp_data['Year'] == year) & (sp_data['Month'] == month)]
    if len(row) > 0:
        return row['Total_Return_Index'].values[0]
    return None

def calc_return_period(start_year, start_month, end_year, end_month):
    """計算兩個日期之間的報酬率"""
    start_idx = get_index_at_date(start_year, start_month)
    end_idx = get_index_at_date(end_year, end_month)
    if start_idx and end_idx:
        return (end_idx / start_idx - 1) * 100
    return None

# 定義擴張期（只需要擴張期，因為我們要分析「衰退前」的報酬）
# 格式：(名稱, 擴張開始年月, 衰退開始年月)
expansion_periods = [
    ("新政復甦", (1933, 3), (1937, 5)),
    ("二戰擴張", (1938, 6), (1945, 2)),
    ("戰後調整", (1945, 10), (1948, 11)),
    ("戰後繁榮", (1949, 10), (1953, 7)),
    ("艾森豪繁榮", (1954, 5), (1957, 8)),
    ("短期復甦", (1958, 4), (1960, 4)),
    ("甘迺迪-詹森", (1961, 2), (1969, 12)),
    ("尼克森擴張", (1970, 11), (1973, 11)),
    ("滯脹復甦", (1975, 3), (1980, 1)),
    ("雷根牛市", (1982, 11), (1990, 7)),
    ("克林頓繁榮", (1991, 3), (2001, 3)),
    ("房地產泡沫", (2001, 11), (2007, 12)),
    ("QE牛市", (2009, 6), (2020, 2)),
    # 疫後復甦 - 2022 雖然技術性衰退但 NBER 未認定，先不納入
]

print("=" * 80)
print("分析 1：用精確時間區段計算「衰退前 N 年」報酬")
print("=" * 80)
print()

results = []

for name, (exp_start_y, exp_start_m), (rec_start_y, rec_start_m) in expansion_periods:
    rec_start = datetime(rec_start_y, rec_start_m, 1)

    # 計算衰退前 1/2/3 年的報酬
    # 衰退前1年 = 衰退開始往前12個月 到 衰退開始
    before_1y = rec_start - relativedelta(months=12)
    before_2y = rec_start - relativedelta(months=24)
    before_3y = rec_start - relativedelta(months=36)

    ret_1y = calc_return_period(before_1y.year, before_1y.month, rec_start_y, rec_start_m)
    ret_2y = calc_return_period(before_2y.year, before_2y.month, before_1y.year, before_1y.month)
    ret_3y = calc_return_period(before_3y.year, before_3y.month, before_2y.year, before_2y.month)

    # 計算整個擴張期的年化報酬
    exp_start = datetime(exp_start_y, exp_start_m, 1)
    months_total = (rec_start.year - exp_start.year) * 12 + (rec_start.month - exp_start.month)
    total_ret = calc_return_period(exp_start_y, exp_start_m, rec_start_y, rec_start_m)
    if total_ret and months_total > 0:
        annualized = ((1 + total_ret/100) ** (12/months_total) - 1) * 100
    else:
        annualized = None

    results.append({
        'name': name,
        'exp_start': f"{exp_start_y}-{exp_start_m:02d}",
        'rec_start': f"{rec_start_y}-{rec_start_m:02d}",
        'months': months_total,
        'ret_1y': ret_1y,
        'ret_2y': ret_2y,
        'ret_3y': ret_3y,
        'total_ret': total_ret,
        'annualized': annualized
    })

# 輸出表格
print(f"{'週期':<15} {'擴張開始':<10} {'衰退開始':<10} {'月數':<6} {'衰退前1年':<12} {'衰退前2年':<12} {'衰退前3年':<12}")
print("-" * 95)

for r in results:
    ret_1y_str = f"{r['ret_1y']:.2f}%" if r['ret_1y'] else "N/A"
    ret_2y_str = f"{r['ret_2y']:.2f}%" if r['ret_2y'] else "N/A"
    ret_3y_str = f"{r['ret_3y']:.2f}%" if r['ret_3y'] else "N/A"
    print(f"{r['name']:<15} {r['exp_start']:<10} {r['rec_start']:<10} {r['months']:<6} {ret_1y_str:<12} {ret_2y_str:<12} {ret_3y_str:<12}")

# 計算統計
ret_1y_list = [r['ret_1y'] for r in results if r['ret_1y'] is not None]
ret_2y_list = [r['ret_2y'] for r in results if r['ret_2y'] is not None]
ret_3y_list = [r['ret_3y'] for r in results if r['ret_3y'] is not None]

print("-" * 95)
print(f"{'平均':<15} {'':<10} {'':<10} {'':<6} {sum(ret_1y_list)/len(ret_1y_list):.2f}%       {sum(ret_2y_list)/len(ret_2y_list):.2f}%       {sum(ret_3y_list)/len(ret_3y_list):.2f}%")

# 正報酬比例
pos_1y = sum(1 for r in ret_1y_list if r > 0) / len(ret_1y_list) * 100
pos_2y = sum(1 for r in ret_2y_list if r > 0) / len(ret_2y_list) * 100
pos_3y = sum(1 for r in ret_3y_list if r > 0) / len(ret_3y_list) * 100
print(f"{'正報酬比例':<15} {'':<10} {'':<10} {'':<6} {pos_1y:.1f}%        {pos_2y:.1f}%        {pos_3y:.1f}%")

print()
print("=" * 80)
print("分析 2：持股水位策略回測")
print("=" * 80)
print()
print("策略定義：")
print("  A: 100% 持股（全程不調整）")
print("  B: 擴張期最後12個月降到 50% 持股")
print("  C: 擴張期最後12個月清倉 0%")
print()

# 回測：計算每個擴張期 + 後續衰退期的總報酬
# 我們需要定義衰退結束日期
recession_ends = {
    "新政復甦": (1938, 6),
    "二戰擴張": (1945, 10),
    "戰後調整": (1949, 10),
    "戰後繁榮": (1954, 5),
    "艾森豪繁榮": (1958, 4),
    "短期復甦": (1961, 2),
    "甘迺迪-詹森": (1970, 11),
    "尼克森擴張": (1975, 3),
    "滯脹復甦": (1980, 7),  # Volcker 1
    "雷根牛市": (1991, 3),
    "克林頓繁榮": (2001, 11),
    "房地產泡沫": (2009, 6),
    "QE牛市": (2020, 4),
}

print(f"{'週期':<15} {'策略A(100%)':<15} {'策略B(50%)':<15} {'策略C(0%)':<15} {'最後1年報酬':<15} {'衰退期報酬':<15}")
print("-" * 100)

strategy_results = []

for name, (exp_start_y, exp_start_m), (rec_start_y, rec_start_m) in expansion_periods:
    rec_start = datetime(rec_start_y, rec_start_m, 1)
    before_1y = rec_start - relativedelta(months=12)

    # 擴張期前段報酬（除了最後12個月）
    ret_early = calc_return_period(exp_start_y, exp_start_m, before_1y.year, before_1y.month)

    # 最後12個月報酬
    ret_last_1y = calc_return_period(before_1y.year, before_1y.month, rec_start_y, rec_start_m)

    # 衰退期報酬
    if name in recession_ends:
        rec_end_y, rec_end_m = recession_ends[name]
        ret_recession = calc_return_period(rec_start_y, rec_start_m, rec_end_y, rec_end_m)
    else:
        ret_recession = None

    if ret_early is None or ret_last_1y is None:
        continue

    # 策略 A: 100% 全程持有
    # 報酬 = 前段 + 最後1年 + 衰退期（複利計算）
    strat_a_exp = (1 + ret_early/100) * (1 + ret_last_1y/100) - 1
    if ret_recession is not None:
        strat_a_total = (1 + strat_a_exp) * (1 + ret_recession/100) - 1
    else:
        strat_a_total = strat_a_exp

    # 策略 B: 50% 最後1年
    # 前段 100% + 最後1年 50%（另 50% 現金）+ 衰退期 50%（另 50% 現金）
    # 簡化假設：現金報酬 = 0
    strat_b_last_1y = ret_last_1y * 0.5  # 只有 50% 曝險
    strat_b_exp = (1 + ret_early/100) * (1 + strat_b_last_1y/100) - 1
    if ret_recession is not None:
        strat_b_rec = ret_recession * 0.5
        strat_b_total = (1 + strat_b_exp) * (1 + strat_b_rec/100) - 1
    else:
        strat_b_total = strat_b_exp

    # 策略 C: 0% 最後1年（完全清倉）
    strat_c_exp = ret_early / 100  # 只有前段
    if ret_recession is not None:
        # 假設衰退結束後再買回
        strat_c_total = strat_c_exp
    else:
        strat_c_total = strat_c_exp

    strat_a_pct = strat_a_total * 100
    strat_b_pct = strat_b_total * 100
    strat_c_pct = strat_c_total * 100

    strategy_results.append({
        'name': name,
        'strat_a': strat_a_pct,
        'strat_b': strat_b_pct,
        'strat_c': strat_c_pct,
        'last_1y': ret_last_1y,
        'recession': ret_recession
    })

    rec_str = f"{ret_recession:.2f}%" if ret_recession else "N/A"
    print(f"{name:<15} {strat_a_pct:>10.2f}%    {strat_b_pct:>10.2f}%    {strat_c_pct:>10.2f}%    {ret_last_1y:>10.2f}%    {rec_str:>12}")

print("-" * 100)

# 計算平均
avg_a = sum(r['strat_a'] for r in strategy_results) / len(strategy_results)
avg_b = sum(r['strat_b'] for r in strategy_results) / len(strategy_results)
avg_c = sum(r['strat_c'] for r in strategy_results) / len(strategy_results)
avg_last = sum(r['last_1y'] for r in strategy_results) / len(strategy_results)
avg_rec = sum(r['recession'] for r in strategy_results if r['recession']) / len([r for r in strategy_results if r['recession']])

print(f"{'平均':<15} {avg_a:>10.2f}%    {avg_b:>10.2f}%    {avg_c:>10.2f}%    {avg_last:>10.2f}%    {avg_rec:>10.2f}%")

print()
print("=" * 80)
print("分析 3：策略勝負統計")
print("=" * 80)
print()

# A vs B
a_better_than_b = sum(1 for r in strategy_results if r['strat_a'] > r['strat_b'])
b_better_than_a = len(strategy_results) - a_better_than_b
print(f"策略 A (100%) vs 策略 B (50%):")
print(f"  A 勝: {a_better_than_b} 次 ({a_better_than_b/len(strategy_results)*100:.1f}%)")
print(f"  B 勝: {b_better_than_a} 次 ({b_better_than_a/len(strategy_results)*100:.1f}%)")
print()

# A vs C
a_better_than_c = sum(1 for r in strategy_results if r['strat_a'] > r['strat_c'])
c_better_than_a = len(strategy_results) - a_better_than_c
print(f"策略 A (100%) vs 策略 C (0%):")
print(f"  A 勝: {a_better_than_c} 次 ({a_better_than_c/len(strategy_results)*100:.1f}%)")
print(f"  C 勝: {c_better_than_a} 次 ({c_better_than_a/len(strategy_results)*100:.1f}%)")
print()

# B vs C
b_better_than_c = sum(1 for r in strategy_results if r['strat_b'] > r['strat_c'])
c_better_than_b = len(strategy_results) - b_better_than_c
print(f"策略 B (50%) vs 策略 C (0%):")
print(f"  B 勝: {b_better_than_c} 次 ({b_better_than_c/len(strategy_results)*100:.1f}%)")
print(f"  C 勝: {c_better_than_b} 次 ({c_better_than_b/len(strategy_results)*100:.1f}%)")

print()
print("=" * 80)
print("分析 4：什麼時候應該減碼？")
print("=" * 80)
print()

# 分析最後1年負報酬的週期
negative_last_1y = [r for r in strategy_results if r['last_1y'] < 0]
positive_last_1y = [r for r in strategy_results if r['last_1y'] >= 0]

print(f"衰退前1年負報酬的週期（{len(negative_last_1y)}/{len(strategy_results)} = {len(negative_last_1y)/len(strategy_results)*100:.1f}%）:")
for r in negative_last_1y:
    print(f"  {r['name']}: {r['last_1y']:.2f}%")

print()
print(f"衰退前1年正報酬的週期（{len(positive_last_1y)}/{len(strategy_results)} = {len(positive_last_1y)/len(strategy_results)*100:.1f}%）:")
for r in positive_last_1y:
    print(f"  {r['name']}: {r['last_1y']:.2f}%")

print()
print("=" * 80)
print("結論")
print("=" * 80)
print()
print(f"1. 衰退前1年平均報酬：{avg_last:.2f}%")
print(f"   - 正報酬機率：{len(positive_last_1y)/len(strategy_results)*100:.1f}%")
print(f"   - 平均正報酬：{sum(r['last_1y'] for r in positive_last_1y)/len(positive_last_1y):.2f}%")
if negative_last_1y:
    print(f"   - 平均負報酬：{sum(r['last_1y'] for r in negative_last_1y)/len(negative_last_1y):.2f}%")
print()
print(f"2. 策略比較（平均報酬）：")
print(f"   - 策略 A (100%): {avg_a:.2f}%")
print(f"   - 策略 B (50%):  {avg_b:.2f}%")
print(f"   - 策略 C (0%):   {avg_c:.2f}%")
print()
print(f"3. 結論：")
if avg_a > avg_b > avg_c:
    print(f"   策略 A > 策略 B > 策略 C")
    print(f"   → 歷史上「不減碼」的報酬最好")
    print(f"   → 但策略 B 可以降低波動風險（少賺一點但少套一點）")
elif avg_b > avg_a:
    print(f"   策略 B > 策略 A")
    print(f"   → 歷史上「減碼到 50%」的報酬更好")
