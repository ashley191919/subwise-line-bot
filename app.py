from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from gemini_client import (
    ask_gemini,
    ask_gemini_with_image
)
from google_sheets import (
    get_expenses,
    get_subscriptions,
    add_expense,
    add_subscription,
)
from expense_service import save_expense
from query_service import (
    query_data,
    get_upcoming_subscriptions,
    format_upcoming_subscriptions
)
from subscription_service import (
    save_subscription,
    get_subscription_analysis,
    format_subscription_analysis,
    get_subscriptions
)
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

VALID_CATEGORIES = {
    "Food",
    "Transport",
    "Entertainment",
    "Shopping",
    "Bills",
    "Health",
    "Education",
    "Subscription",
    "Other"
}

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

def create_main_menu_quick_reply():
    """
    建立 SubWise 主首頁的 LINE Quick Reply。
    """

    return QuickReply(
        items=[
            QuickReplyItem(
                action=MessageAction(
                    label="💰 記帳",
                    text="記帳"
                )
            ),
            QuickReplyItem(
                action=MessageAction(
                    label="🔎 查詢",
                    text="查詢"
                )
            ),
            QuickReplyItem(
                action=MessageAction(
                    label="📊 分析",
                    text="分析"
                )
            ),
            QuickReplyItem(
                action=MessageAction(
                    label="🔔 訂閱",
                    text="訂閱"
                )
            ),
            QuickReplyItem(
                action=MessageAction(
                    label="⏰ 扣款提醒",
                    text="扣款提醒"
                )
            )
        ]
    )

def get_main_menu():
    """
    回傳 SubWise 互動式首頁。
    """

    return (
        "🤖 SubWise\n\n"
        "嗨！我是你的智慧生活記帳管家 👋\n\n"
        "你想做什麼？\n\n"
        "💰 記帳｜記錄日常消費\n"
        "🔎 查詢｜查看消費與訂閱\n"
        "📊 分析｜了解你的消費狀況\n"
        "🔔 訂閱｜管理週期性服務\n"
        "⏰ 扣款提醒｜查看近期扣款\n\n"
        "👇 點選下方功能開始"
    )  

def create_query_quick_reply():
    """
    建立查詢功能的 LINE Quick Reply。
    """

    return QuickReply(
        items=[
            QuickReplyItem(
                action=MessageAction(
                    label="💰 消費",
                    text="查詢消費"
                )
            ),
            QuickReplyItem(
                action=MessageAction(
                    label="🔔 訂閱",
                    text="查詢訂閱"
                )
            )
        ]
    )

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

    elif text in ["查詢", "查詢資料"]:
        return (
            "🔎 SubWise 查詢\n\n"
            "你想查看什麼？\n\n"
            "💰 消費｜查看消費紀錄\n"
            "🔔 訂閱｜查看目前訂閱\n\n"
            "👇 點選下方選項開始"
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
    
    elif text in ["扣款提醒", "即將扣款", "近期扣款"]:
        return process_upcoming_subscriptions()

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

def process_upcoming_subscriptions():
    """
    查詢最近 7 天內即將扣款的訂閱。
    """

    print("⏰ 開始查詢近期扣款訂閱")

    try:
        # 取得所有訂閱
        records = get_subscriptions()

        print(
            f"📦 訂閱資料筆數：{len(records)}"
        )

        # 找出 7 天內即將扣款的訂閱
        upcoming = get_upcoming_subscriptions(
            records,
            days=7
        )

        print(
            f"⏰ 即將扣款筆數：{len(upcoming)}"
        )

        # 整理成 LINE 顯示文字
        return format_upcoming_subscriptions(
            upcoming
        )

    except Exception as e:

        print(
            f"❌ 扣款提醒查詢失敗：{e}"
        )

        return (
            "❌ 扣款提醒查詢失敗\n\n"
            "⚠️ 目前無法取得訂閱資料，"
            "請稍後再試。"
        )

def get_quick_reply(text):
    """
    根據使用者輸入決定是否顯示 Quick Reply。
    """

    text = text.lower().strip()

    if text in ["help", "menu", "功能", "選單"]:
        return create_main_menu_quick_reply()

    if text in ["查詢", "查詢資料"]:
        return create_query_quick_reply()

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

def find_expense_matches(data):
    """
    根據 Gemini 提供的日期與金額，
    找出可能符合的消費資料。
    """

    from google_sheets import get_expenses

    records = get_expenses()

    target_date = data.get("date")
    target_amount = data.get("amount")

    if target_amount is None:
        target_amount = data.get("old_amount")

    matches = []

    for index, record in enumerate(records, start=2):

        record_date = str(
            record.get("Date", "")
        ).strip()

        record_amount = record.get(
            "Amount",
            0
        )

        try:
            record_amount = float(record_amount)
        except (TypeError, ValueError):
            continue

        if target_date:
            if record_date != target_date:
                continue

        if target_amount is not None:
            try:
                if record_amount != float(target_amount):
                    continue
            except (TypeError, ValueError):
                continue

        matches.append({
            "row": index,
            "record": record
        })

    return matches

def edit_expense(data):
    """
    修改指定的消費資料。
    """

    from google_sheets import update_expense

    matches = find_expense_matches(data)

    if not matches:
        return (
            "🔎 找不到符合條件的消費資料。\n\n"
            "請提供更明確的日期或金額。"
        )

    if len(matches) > 1:
        return (
            "⚠️ 找到多筆符合的消費資料。\n\n"
            "為避免修改錯誤資料，"
            "請提供更明確的日期或金額。"
        )

    match = matches[0]

    row = match["row"]
    record = match["record"]

    field = data.get("field")
    value = data.get("value")

    if field == "category":
        if value not in VALID_CATEGORIES:
            return (
                f"⚠️「{value}」不是目前支援的消費分類。\n\n"
                "目前分類有：\n\n"
                "🍜 Food｜餐飲\n"
                "🚇 Transport｜交通\n"
                "🎮 Entertainment｜娛樂\n"
                "🛍️ Shopping｜購物\n"
                "💡 Bills｜生活帳單\n"
                "❤️ Health｜醫療保健\n"
                "📚 Education｜學習\n"
                "🔔 Subscription｜訂閱\n"
                "📦 Other｜其他\n\n"
                "請問你想把它改成哪一個分類？"
            )

    column_map = {
        "category": 2,
        "amount": 3,
        "item": 4,
        "note": 5
    }

    if field not in column_map:
        return "⚠️ 目前不支援修改這個欄位。"

    column = column_map[field]

    update_expense(
        row,
        column,
        value
    )

    if field == "category":
        field_text = "分類"
    elif field == "amount":
        field_text = "金額"
    elif field == "item":
        field_text = "項目"
    elif field == "note":
        field_text = "備註"
    else:
        field_text = field

    return (
        "✏️ 記帳修改成功！\n\n"
        f"📅 日期：{record.get('Date', '')}\n"
        f"💵 金額：NT${record.get('Amount', '')}\n"
        f"📝 {field_text}已修改為：{value}"
    )

def delete_expense(data):
    """
    刪除指定的消費資料。
    """

    from google_sheets import delete_expense as delete_sheet_row

    # Gemini 使用 old_amount 表示「原本的消費金額」。
    # find_expense_matches() 使用 amount 搜尋，
    # 因此這裡先轉換成 amount。
    search_data = data.copy()

    if (
        search_data.get("amount") is None
        and search_data.get("old_amount") is not None
    ):
        search_data["amount"] = search_data.get("old_amount")

    matches = find_expense_matches(search_data)

    if not matches:
        return (
            "🔎 找不到符合條件的消費資料。\n\n"
            "請提供更明確的日期或金額。"
        )

    if len(matches) > 1:
        return (
            "⚠️ 找到多筆符合的消費資料。\n\n"
            "為避免誤刪，"
            "請提供更明確的日期或金額。"
        )

    match = matches[0]

    row = match["row"]
    record = match["record"]

    delete_sheet_row(row)

    return (
        "🗑️ 記帳刪除成功！\n\n"
        f"📅 日期：{record.get('Date', '')}\n"
        f"📂 分類：{record.get('Category', '')}\n"
        f"💵 金額：NT${record.get('Amount', '')}\n"
        f"📝 項目：{record.get('Note', '')}"
    )

def process_ai_message(text):
    """使用 Gemini 判斷使用者意圖，並回傳 AI 回覆。"""

    data = ask_gemini(text)

    if not data:
        return "⚠️ SubWise AI 暫時無法處理這則訊息，請稍後再試。"

    data_type = data.get("type")

    print(f"📦 Gemini JSON：{data}")

    if data_type == "invalid_category":

        category = data.get("category", "未知分類")

        return (
            f"⚠️「{category}」不是目前支援的消費分類。\n\n"
            "目前分類有：\n\n"
            "🍜 Food｜餐飲\n"
            "🚇 Transport｜交通\n"
            "🎮 Entertainment｜娛樂\n"
            "🛍️ Shopping｜購物\n"
            "💡 Bills｜生活帳單\n"
            "❤️ Health｜醫療保健\n"
            "📚 Education｜學習\n"
            "🔔 Subscription｜訂閱\n"
            "📦 Other｜其他\n\n"
            "請問你想把它改成哪一個分類？"
        )

    elif data_type == "chat":
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

    elif data_type == "subscription_analysis":

        print("📊 Gemini 已辨識為訂閱分析")
        print("🔔 開始分析 Subscription Google Sheets...")

        try:

            days = data.get("days", 7)

            analysis = get_subscription_analysis(
                days
            )

            print("✅ 訂閱分析完成")
            print(f"📦 分析資料：{analysis}")

            return format_subscription_analysis(
                analysis,
                days
            )

        except Exception as e:

            print(f"❌ 訂閱分析失敗：{e}")

            return (
                "❌ 訂閱分析失敗\n\n"
                "⚠️ 目前無法取得訂閱分析資料，"
                "請稍後再試。"
            )

    elif data_type == "expense_update":

        print("✏️ Gemini 已辨識為修改消費")

        try:

            return edit_expense(data)

        except Exception as e:

            print(f"❌ 修改消費失敗：{e}")

            return (
                "❌ 修改失敗\n\n"
                "⚠️ 目前無法修改這筆消費，"
                "請稍後再試。"
            )

    elif data_type == "expense_delete":

        print("🗑️ Gemini 已辨識為刪除消費")

        try:

            return delete_expense(data)

        except Exception as e:

            print(f"❌ 刪除消費失敗：{e}")

            return (
                "❌ 刪除失敗\n\n"
                "⚠️ 目前無法刪除這筆消費，"
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

    print("🔥 Render 收到 LINE 訊息")
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

            # Gemini 無法判斷分類時，使用 Other 作為預設分類
            if not data.get("category"):
                print("⚠️ Gemini 未辨識消費分類，使用 Other")
                data["category"] = "Other"

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