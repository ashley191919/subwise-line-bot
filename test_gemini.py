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

    print(f"Gemini：{reply}")