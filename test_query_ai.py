from gemini_client import ask_gemini
from query_service import query_data


print("🤖 SubWise AI Query")
print("=" * 50)
print("輸入 exit 或 quit 離開")
print("=" * 50)


while True:

    prompt = input("\n你：")

    if prompt.lower() in ["exit", "quit"]:
        print("👋 SubWise AI Query 結束！")
        break

    if not prompt.strip():
        print("⚠️ 請輸入問題。")
        continue

    print("\n🤖 Gemini 思考中...")

    data = ask_gemini(prompt)

    if not data:
        print("❌ Gemini 沒有回傳有效資料。")
        continue

    print("\n📦 Gemini JSON：")
    print(data)

    data_type = data.get("type")

    # -------------------------
    # Query
    # -------------------------

    if data_type == "query":

        print("\n🔎 執行 Google Sheets 查詢...")

        result = query_data(data)

        print("\n📌 SubWise 查詢結果：")
        print(result)

    # -------------------------
    # Chat
    # -------------------------

    elif data_type == "chat":

        message = data.get("message", "")

        print("\n💬 SubWise：")
        print(message)

    # -------------------------
    # Expense
    # -------------------------

    elif data_type == "expense":

        print("\n💰 偵測到消費資料")

        print(
            f"分類：{data.get('category')}"
        )

        print(
            f"金額：{data.get('amount')}"
        )

        print(
            f"項目：{data.get('item')}"
        )

    # -------------------------
    # Subscription
    # -------------------------

    elif data_type == "subscription":

        print("\n🔔 偵測到訂閱資料")

        print(
            f"服務：{data.get('name')}"
        )

        print(
            f"金額：{data.get('amount')}"
        )

        print(
            f"扣款週期：{data.get('billing_cycle')}"
        )

        print(
            f"下次扣款：{data.get('next_billing_date')}"
        )

    else:

        print("⚠️ 未知的資料類型。")