from gemini_client import ask_gemini


print("🔎 SubWise Query 測試")
print("=" * 50)
print("測試 Gemini 是否能正確判斷查詢意圖")
print("輸入 exit 或 quit 離開")
print("=" * 50)


while True:

    prompt = input("\n你：")

    if prompt.lower() in ["exit", "quit"]:
        print("👋 Query 測試結束！")
        break

    if not prompt.strip():
        print("⚠️ 請輸入問題。")
        continue

    print("\n🤖 Gemini 思考中...\n")

    reply = ask_gemini(prompt)

    print("📦 Gemini JSON：")
    print(reply)

    if reply:
        print("\n📌 Python 已成功解析：")
        print(f"類型：{reply.get('type')}")

        if reply.get("type") == "query":
            print(f"查詢目標：{reply.get('target')}")
            print(f"查詢期間：{reply.get('period')}")
            print(f"關鍵字：{reply.get('keyword')}")

        elif reply.get("type") == "expense":
            print(f"分類：{reply.get('category')}")
            print(f"金額：{reply.get('amount')}")
            print(f"項目：{reply.get('item')}")
            print(f"日期：{reply.get('date')}")

        elif reply.get("type") == "subscription":
            print(f"服務：{reply.get('name')}")
            print(f"金額：{reply.get('amount')}")
            print(f"扣款週期：{reply.get('billing_cycle')}")
            print(f"下次扣款：{reply.get('next_billing_date')}")

        elif reply.get("type") == "chat":
            print(f"AI 回覆：{reply.get('message')}")