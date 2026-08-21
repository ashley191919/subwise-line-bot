from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from gemini_client import (
    ask_gemini,
    ask_gemini_with_image
)
from expense_service import save_expense
from query_service import query_data
from subscription_service import save_subscription
from analysis_service import (
    get_expense_analysis,
    format_analysis_result,
    generate_spending_insight
)
from menu_service import get_main_menu

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    QuickReplyItem,
    MessageAction,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent
)
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

def create_analysis_quick_reply():
    """
    建立消費分析的 LINE Quick Reply。
    """

    return QuickReply(
        items=[
            QuickReplyItem(
                action=MessageAction(
                    label="📅 今天",
                    text="今天"
                )
            ),
            QuickReplyItem(
                action=MessageAction(
                    label="📆 本週",
                    text="本週"
                )
            ),
            QuickReplyItem(
                action=MessageAction(
                    label="🗓️ 本月",
                    text="本月"
                )
            )
        ]
    )

def process_feature_command(text):
    """
    處理主選單中的功能入口。
    """

    text = text.lower().strip()

    if text in ["記帳", "帳目", "新增記帳"]:
        return (
            "💰 SubWise 記帳\n\n"
            "直接告訴我你花了多少錢，例如：\n\n"
            "「午餐 120 元」\n"
            "「今天搭捷運 50 元」\n\n"
            "🤖 我會幫你自動整理消費資訊。"
        )

    elif text in ["分析", "消費分析", "支出分析"]:
        return (
            "📊 SubWise 消費分析\n\n"
            "請選擇你想分析的期間：\n\n"
            "📅 今天\n"
            "📆 本週\n"
            "🗓️ 本月\n\n"
            "你也可以直接輸入：\n"
            "「今天」\n"
            "「本週」\n"
            "「本月」"
        )

    elif text in ["發票", "發票辨識", "收據", "收據辨識"]:
        return (
            "📷 SubWise 發票辨識\n\n"
            "直接傳送發票或收據照片給我，\n"
            "我會協助辨識其中的消費資訊。\n\n"
            "🚧 多模態辨識功能開發中"
        )

    elif text in ["訂閱", "訂閱管理", "訂閱服務"]:
        return (
            "🔔 SubWise 訂閱管理\n\n"
            "你可以管理 Netflix、Spotify、YouTube Premium\n"
            "等週期性訂閱服務。\n\n"
            "🚧 訂閱管理功能開發中"
        )

    elif text in ["今天", "今日"]:
        return process_analysis_period("today")

    elif text in ["本週", "這週", "這周"]:
        return process_analysis_period("week")

    elif text in ["本月", "這個月"]:
        return process_analysis_period("month")

    return None

def process_analysis_period(period):
    """
    根據指定期間執行消費分析。
    """

    print(f"📊 快速分析入口：{period}")

    try:
        # 取得分析資料
        analysis = get_expense_analysis(period)

        print("✅ 消費分析完成")
        print(f"📦 分析資料：{analysis}")

        # 整理分析結果
        message = format_analysis_result(
            analysis
        )

        # 產生智慧提醒
        insight = generate_spending_insight(
            analysis
        )

        return (
            f"{message}\n\n"
            f"{insight}"
        )

    except Exception as e:

        print(
            f"❌ 快速分析失敗：{e}"
        )

        return (
            "❌ 分析失敗\n\n"
            "⚠️ 目前無法取得消費分析資料，"
            "請稍後再試。"
        )

def get_quick_reply(text):
    """
    根據使用者輸入決定是否顯示 Quick Reply。
    """

    text = text.lower().strip()

    if text in ["分析", "消費分析", "支出分析"]:
        return create_analysis_quick_reply()

    return None

def process_command(text):
    """根據使用者輸入的指令，回傳對應的回覆內容。"""

    feature_reply = process_feature_command(text)

    if feature_reply:
        return feature_reply

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

    elif text.lower() in ["help", "menu", "功能", "選單"]:
        return get_main_menu()

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

        print("🔔 Gemini 已辨識為訂閱資料")
        print("📝 開始寫入 Subscription Google Sheets...")

        result = save_subscription(data)

        if result:

            print("✅ 訂閱資料已成功寫入 Google Sheets")

            return (
                "✅ 訂閱建立成功！\n\n"
                f"📌 服務：{result.get('name')}\n"
                f"💰 金額：NT${result.get('amount')}\n"
                f"🔄 扣款週期：{result.get('billing_cycle')}\n"
                f"📅 下次扣款：{result.get('next_billing_date')}"
            )

        else:

            return (
                "❌ 訂閱建立失敗\n\n"
                "⚠️ 訂閱資料沒有成功寫入 Google Sheets，請稍後再試。"
            )

    elif data_type == "query":

        print("🔎 Gemini 已辨識為資料查詢")
        print("📊 開始透過 query_service 查詢 Google Sheets...")

        try:
            result = query_data(data)

            print("✅ Google Sheets 查詢完成")
            print(f"📦 查詢結果：{result}")

            return result

        except Exception as e:
            print(f"❌ Google Sheets 查詢失敗：{e}")

            return (
                "❌ 查詢失敗\n\n"
                "⚠️ 目前無法取得 Google Sheets 的資料，"
                "請稍後再試。"
            )

    elif data_type == "analysis":

        print("📊 Gemini 已辨識為消費分析")
        print("📈 開始透過 analysis_service 分析 Google Sheets...")

        try:
            period = data.get("period", "month")

            # 1. 取得消費分析資料
            analysis = get_expense_analysis(period)

            print("✅ Google Sheets 分析完成")
            print(f"📦 分析資料：{analysis}")

            # 2. 整理成 LINE 可閱讀格式
            message = format_analysis_result(analysis)

            # 3. 產生智慧消費提醒
            insight = generate_spending_insight(analysis)

            # 4. 合併回覆
            return (
                f"{message}\n\n"
                f"{insight}"
            )

        except Exception as e:
            print(f"❌ Google Sheets 分析失敗：{e}")

            return (
                "❌ 分析失敗\n\n"
                "⚠️ 目前無法取得消費分析資料，"
                "請稍後再試。"
            )

    else:
        return "⚠️ SubWise 暫時無法判斷你的需求。"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    # 取得使用者輸入
    text = event.message.text.strip()

    print("🔥 DAY 12 TEST - Render 收到 LINE 訊息")
    print(f"📩 LINE 收到訊息：{text}")

    # 固定指令
    fixed_commands = [
        "hi",
        "hello",
        "你好",
        "哈囉",
        "help",
        "menu",
        "功能",
        "選單",
        "about",
        "ping",

        # 功能入口
        "記帳",
        "帳目",
        "新增記帳",

        "分析",
        "消費分析",
        "支出分析",

        "今天",
        "今日",
        "本週",
        "這週",
        "這周",
        "本月",
        "這個月",

        "發票",
        "發票辨識",
        "收據",
        "收據辨識",

        "訂閱",
        "訂閱管理",
        "訂閱服務"
    ]

    # 判斷訊息要走固定指令還是 Gemini
    if text.lower() in fixed_commands:
        print("📌 使用固定指令處理")
        reply_text = process_command(text)

    else:
        print("🤖 交給 Gemini AI 處理")
        reply_text = process_ai_message(text)

    # 回覆 LINE
    quick_reply = get_quick_reply(text)

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        message = TextMessage(
            text=reply_text,
            quick_reply=quick_reply
        )

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    message
                ]
            )
        )

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):

    print("📷 SubWise 收到圖片訊息")
    print(f"🆔 LINE Message ID：{event.message.id}")

    try:

        # 1. 從 LINE 取得圖片
        with ApiClient(configuration) as api_client:

            line_bot_api = MessagingApiBlob(api_client)

            image_bytes = line_bot_api.get_message_content(
                event.message.id
            )

        print("✅ 成功取得 LINE 圖片")
        print(f"📦 圖片大小：{len(image_bytes)} bytes")

        # 2. 將圖片交給 Gemini
        print("🤖 開始進行 Gemini 圖片辨識...")

        data = ask_gemini_with_image(
            image_bytes,
            "image/jpeg"
        )

        print("📦 Gemini 圖片辨識結果：")
        print(data)

        # 3. 判斷 Gemini 是否辨識成功
        if not data:

            print("❌ Gemini 沒有回傳有效資料")

            with ApiClient(configuration) as api_client:

                line_bot_api = MessagingApi(api_client)

                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessage(
                                text=(
                                    "❌ 發票辨識失敗\n\n"
                                    "⚠️ AI 沒有取得有效的消費資料，"
                                    "請再試一次。"
                                )
                            )
                        ]
                    )
                )

            return

        # 4. 如果 Gemini 判斷為 expense
        if data.get("type") == "expense":

            print("💰 Gemini 辨識為消費資料")

            success = save_expense(data)

            if success:

                print("✅ 發票消費資料已寫入 Google Sheets")

                reply_text = (
                    "✅ 發票辨識成功，已完成記帳！\n\n"
                    f"📅 日期：{data.get('date') or '未辨識'}\n"
                    f"📂 分類：{data.get('category') or '未分類'}\n"
                    f"💵 金額：NT${data.get('amount') or '未辨識'}\n"
                    f"📝 項目：{data.get('item') or '未辨識'}"
                )

            else:

                print("❌ 發票消費資料寫入失敗")

                reply_text = (
                    "⚠️ 發票辨識成功，但記帳失敗。\n\n"
                    "請稍後再試。"
                )

        else:

            print("ℹ️ 圖片不是可建立的消費資料")

            reply_text = (
                "ℹ️ 這張圖片目前無法建立消費紀錄。\n\n"
                "請確認你傳送的是發票或收據照片。"
            )

        # 5. 回覆 LINE
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

    except Exception as e:

        print(f"❌ LINE 圖片處理失敗：{e}")

        try:

            with ApiClient(configuration) as api_client:

                line_bot_api = MessagingApi(api_client)

                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessage(
                                text=(
                                    "❌ 發票圖片處理失敗\n\n"
                                    "⚠️ 系統暫時無法處理這張圖片，"
                                    "請稍後再試。"
                                )
                            )
                        ]
                    )
                )

        except Exception as reply_error:

            print(f"❌ LINE 錯誤訊息回覆失敗：{reply_error}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)