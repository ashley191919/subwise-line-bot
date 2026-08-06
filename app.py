from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv

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
            "SubWise\n"
            "AI 智慧記帳與訂閱管理管家"
        )

    elif text.lower() == "ping":
        return "Pong! 🏓"

    else:
        return (
            f"你剛剛說：{text}\n\n"
            "💡 提示：輸入 help 或 menu 查看目前可使用的功能。"
        )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    # 取得使用者輸入
    text = event.message.text

    # 交給 Command Router 處理
    reply_text = process_command(text)

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