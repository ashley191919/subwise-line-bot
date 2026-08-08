from google_sheets import (
    add_expense,
    get_expenses,
    update_expense,
    delete_expense
)


print("🚀 開始測試 Google Sheets 資料層")
print("=" * 50)


# 1. Create
print("1️⃣ Create：新增資料")

add_expense(
    "2026-08-08",
    "Transport",
    50,
    "MRT"
)

print("✅ 新增成功")


# 2. Read
print("\n2️⃣ Read：讀取資料")

expenses = get_expenses()

for expense in expenses:
    print(expense)

print(f"✅ 目前共有 {len(expenses)} 筆資料")


print("\n🎯 Google Sheets 資料層測試完成！")