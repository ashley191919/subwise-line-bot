from google_sheets import query_data


print("🔎 SubWise Google Sheets Query Service")
print("=" * 50)


print("\n📊 消費資料")
expenses = query_data("expense")

for expense in expenses:
    print(expense)


print("\n🔔 訂閱資料")
subscriptions = query_data("subscription")

for subscription in subscriptions:
    print(subscription)