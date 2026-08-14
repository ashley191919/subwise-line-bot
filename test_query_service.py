from query_service import query_data


print("🧪 SubWise Query Service 測試")
print("=" * 50)

test_data = {
    "type": "query",
    "target": "expense",
    "period": "month",
    "keyword": None,
}

print("\n📦 測試 Query JSON：")
print(test_data)

print("\n🔎 開始查詢 Google Sheets...")

try:
    result = query_data(test_data)

    print("\n📌 查詢結果：")
    print(result)

    print("\n✅ Query Service 測試完成")

except Exception as e:
    print("\n❌ Query Service 測試失敗")
    print(f"錯誤：{e}")