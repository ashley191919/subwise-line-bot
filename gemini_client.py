import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

SYSTEM_PROMPT = """
你是 SubWise，一個 AI 智慧記帳與訂閱管理管家。

你的主要工作是協助使用者：

1. 管理日常消費
2. 分析消費類別
3. 管理訂閱服務
4. 提醒即將發生的訂閱扣款
5. 提供簡單、實用的財務管理建議

請遵守以下規則：

- 使用繁體中文回答
- 回覆簡潔、容易理解
- 如果使用者提供消費資訊，可以協助判斷消費類別
- 如果使用者提到 Netflix、Spotify、ChatGPT 等服務，優先判斷是否屬於訂閱服務
- 不要自行捏造使用者沒有提供的消費金額、日期或訂閱資訊
- 如果資訊不足，請向使用者詢問必要資訊
- 不需要回答與記帳、消費或訂閱管理無關的複雜問題
"""


def ask_gemini(prompt):
    """傳送文字給 SubWise AI，並回傳 Gemini 回覆。"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"{SYSTEM_PROMPT}\n\n使用者問題：{prompt}"
        )

        return response.text

    except Exception as e:
        print(f"❌ Gemini API 發生錯誤：{e}")

        return (
            "⚠️ SubWise AI 暫時無法回應。\n\n"
            "可能原因：\n"
            "• Gemini API 額度不足\n"
            "• 網路連線異常\n"
            "• AI 服務暫時忙碌\n\n"
            "請稍後再試。"
        )