from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from gemini_client import ask_gemini
from expense_service import save_expense

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

load_dotenv()
app = Flask(__name__)
configuration = Configuration(
    access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
)

handler = WebhookHandler(
    os.getenv("LINE_CHANNEL_SECRET")
)

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "SubWise Backend is running!"
    })

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK"

def process_command(text):
    """根據使用者輸入的指令，回傳對應的回覆內容。"""
    greetings = ["hi", "hello", "你好", "哈囉"]
    if text.lower() in greetings:
        return (
            "👋 歡迎使用 SubWise！\n\n"
            "我是你的 AI 智慧記帳與訂閱管理管家 🤖\n\n"
            "目前可以使用：\n"
            "📖 help / menu 查看功能\n"
            "ℹ️ about  關於 SubWise\n"
            "🏓 ping   測試 Bot 是否正常\n\n"
            "更多功能即將登場！"
        )

    elif text.lower() in ["help", "menu"]:
        return (
            "📒 SubWise 功能選單\n\n"
            "🤖 about － 關於 SubWise\n"
            "🏓 ping － 測試 Bot\n"
            "💰 記帳（開發中）\n"
            "📷 發票辨識（開發中）\n"
            "🔔 訂閱提醒（開發中）"
        )

    elif text.lower() == "about":
        return (
            "🤖 SubWise\n\n"
            "AI 智慧記帳與訂閱管理管家\n\n"
            "目前功能：\n"
            "✅ LINE Bot 對話\n"
            "✅ 指令管理\n"
            "🚧 AI 記帳開發中\n"
            "🚧 發票辨識開發中\n"
            "🚧 訂閱提醒開發中"
        )

    elif text.lower() == "ping":
        return "Pong! 🏓"

    else:
        return (
            f"你剛剛說：{text}\n\n"
            "💡 提示：輸入 help 或 menu 查看目前可使用的功能。"
        )

def process_ai_message(text):
    """使用 Gemini 判斷使用者意圖，並回傳 AI 回覆。"""

    data = ask_gemini(text)

    if not data:
        return "⚠️ SubWise AI 暫時無法處理這則訊息，請稍後再試。"

    data_type = data.get("type")

    print(f"📦 Gemini JSON：{data}")

    if data_type == "chat":
        return data.get(
            "message",
            "🤖 我是 SubWise，你的 AI 智慧記帳與訂閱管理管家。"
        )

    elif data_type == "expense":

        print("💰 Gemini 已辨識為消費資料")
        print("📝 開始寫入 Google Sheets...")

        success = save_expense(data)

        if success:
            return (
                "✅ 記帳成功！\n\n"
                f"📅 日期：{data.get('date')}\n"
                f"📂 分類：{data.get('category')}\n"
                f"💵 金額：NT${data.get('amount')}\n"
                f"📝 項目：{data.get('item')}"
            )

        else:
            return (
                "❌ 記帳失敗\n\n"
                "⚠️ 消費資料沒有成功寫入 Google Sheets，"
                "請稍後再試。"
            )

    elif data_type == "subscription":
        return (
            "🔔 已辨識為訂閱資料。\n\n"
            f"📌 服務：{data.get('name')}\n"
            f"💰 金額：NT${data.get('amount')}\n"
            f"🔄 扣款週期：{data.get('billing_cycle')}\n"
            f"📅 下次扣款：{data.get('next_billing_date')}\n\n"
            "🚧 Day 12 正在整合 Google Sheets..."
        )

    elif data_type == "query":
        return (
            "🔎 已辨識為資料查詢。\n\n"
            f"📊 查詢目標：{data.get('target')}\n"
            f"📅 查詢期間：{data.get('period')}\n"
            f"🔍 關鍵字：{data.get('keyword')}\n\n"
            "🚧 Day 12 正在整合查詢服務..."
        )

    else:
        return "⚠️ SubWise 暫時無法判斷你的需求。"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    # 取得使用者輸入
    text = event.message.text.strip()

    print(f"📩 LINE 收到訊息：{text}")

    # 固定指令
    fixed_commands = [
        "hi",
        "hello",
        "你好",
        "哈囉",
        "help",
        "menu",
        "about",
        "ping"
    ]

    # 判斷訊息要走固定指令還是 Gemini
    if text.lower() in fixed_commands:
        print("📌 使用固定指令處理")
        reply_text = process_command(text)

    else:
        print("🤖 交給 Gemini AI 處理")
        reply_text = process_ai_message(text)

    # 回覆 LINE
    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=reply_text
                    )
                ]
            )
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)