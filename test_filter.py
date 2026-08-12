from google_sheets import get_expenses
from google_sheets import filter_expenses_by_period


expenses = get_expenses()

print("🔎 SubWise 消費日期篩選測試")
print("=" * 50)


for period in ["today", "yesterday", "week", "month", "all"]:

    print(f"\n📅 查詢期間：{period}")

    results = filter_expenses_by_period(
        expenses,
        period
    )

    for expense in results:
        print(expense)

    print(f"共找到 {len(results)} 筆資料")