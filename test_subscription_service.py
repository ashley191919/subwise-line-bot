from subscription_service import save_subscription, get_subscriptions


print("🧪 SubWise Subscription Service 測試")
print("=" * 50)


test_data = {
    "type": "subscription",
    "name": "Spotify",
    "amount": 199,
    "billing_cycle": "monthly",
    "next_billing_date": "2026-09-01",
    "category": "Subscription",
    "note": "Day 14 測試"
}


print("\n📦 測試資料：")
print(test_data)


print("\n🚀 開始寫入 Google Sheets...")


success = save_subscription(test_data)


print("\n📌 測試結果：")


if success:
    print("✅ 訂閱資料寫入成功")

else:
    print("❌ 訂閱資料寫入失敗")


print("\n🔎 讀取目前訂閱資料...")


subscriptions = get_subscriptions()


print("\n📋 Google Sheets 訂閱資料：")


for subscription in subscriptions:
    print(subscription)