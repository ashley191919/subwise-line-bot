from google_sheets import get_subscriptions


print("🔔 SubWise 訂閱資料測試")
print("=" * 50)

subscriptions = get_subscriptions()

for subscription in subscriptions:
    print(subscription)