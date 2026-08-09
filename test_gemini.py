from gemini_client import ask_gemini


print("🤖 SubWise Gemini Chat")
print("=" * 50)
print("輸入問題與 Gemini 對話")
print("輸入 exit 或 quit 離開")
print("=" * 50)

while True:

    prompt = input("\n你：")

    if prompt.lower() in ["exit", "quit"]:
        print("👋 Gemini Chat 結束！")
        break

    if not prompt.strip():
        print("⚠️ 請輸入問題。")
        continue

    print("🤖 Gemini 思考中...")

    reply = ask_gemini(prompt)

    if not reply:
        print("❌ 無法解析 Gemini 回覆")
        continue

    print("\nGemini JSON：")
    print(reply)

    data_type = reply.get("type")

    print("\n📌 Python 已成功解析：")

    # -------------------------
    # Expense：消費資料
    # -------------------------
    if data_type == "expense":

        print(f"類型：{reply.get('type')}")
        print(f"分類：{reply.get('category')}")
        print(f"金額：{reply.get('amount')}")
        print(f"項目：{reply.get('item')}")
        print(f"日期：{reply.get('date')}")
        print(f"備註：{reply.get('note')}")

    # -------------------------
    # Subscription：訂閱資料
    # -------------------------
    elif data_type == "subscription":

        print(f"類型：{reply.get('type')}")
        print(f"服務：{reply.get('name')}")
        print(f"金額：{reply.get('amount')}")
        print(f"扣款週期：{reply.get('billing_cycle')}")
        print(f"下次扣款：{reply.get('next_billing_date')}")
        print(f"分類：{reply.get('category')}")
        print(f"備註：{reply.get('note')}")

    # -------------------------
    # Chat：一般對話
    # -------------------------
    elif data_type == "chat":

        print(f"類型：{reply.get('type')}")
        print(f"AI 回覆：{reply.get('message')}")

    # -------------------------
    # 未知資料類型
    # -------------------------
    else:

        print(f"⚠️ 未知的資料類型：{data_type}")
        print("完整資料：")
        print(reply)