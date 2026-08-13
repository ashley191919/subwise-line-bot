from expense_service import save_expense


print("🧪 SubWise Expense Service 測試")
print("=" * 50)


test_data = {
    "type": "expense",
    "date": "2026-08-13",
    "category": "Food",
    "amount": 120,
    "item": "午餐",
    "note": ""
}


print("\n📦 測試資料：")
print(test_data)


print("\n🚀 開始透過 expense_service 寫入 Google Sheets...")


result = save_expense(test_data)


print("\n📌 測試結果：")

if result:
    print("✅ 測試成功：消費資料已寫入 Google Sheets")
else:
    print("❌ 測試失敗：消費資料沒有寫入")