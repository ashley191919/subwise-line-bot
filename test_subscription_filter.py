from google_sheets import get_subscriptions
from google_sheets import filter_subscriptions_by_keyword


subscriptions = get_subscriptions()

print("🔎 SubWise 訂閱關鍵字搜尋")
print("=" * 50)


for keyword in ["Netflix", "Spotify", None]:

    print(f"\n🔍 搜尋：{keyword}")

    results = filter_subscriptions_by_keyword(
        subscriptions,
        keyword
    )

    for subscription in results:
        print(subscription)

    print(f"共找到 {len(results)} 筆")