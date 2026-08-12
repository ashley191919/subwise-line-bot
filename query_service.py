from datetime import date, timedelta

from google_sheets import get_expenses, get_subscriptions


def filter_expenses(records, period="all"):
    """依照指定期間篩選消費資料。"""

    today = date.today()

    if period == "today":
        start_date = today
        end_date = today

    elif period == "yesterday":
        yesterday = today - timedelta(days=1)
        start_date = yesterday
        end_date = yesterday

    elif period == "week":
        start_date = today - timedelta(days=6)
        end_date = today

    elif period == "month":
        start_date = today.replace(day=1)
        end_date = today

    else:
        return records

    filtered = []

    for record in records:
        record_date = record.get("Date")

        if not record_date:
            continue

        try:
            record_date = date.fromisoformat(str(record_date))
        except ValueError:
            continue

        if start_date <= record_date <= end_date:
            filtered.append(record)

    return filtered


def search_subscriptions(records, keyword=None):
    """依照關鍵字搜尋訂閱資料。"""

    if not keyword:
        return records

    keyword = str(keyword).strip().lower()

    results = []

    for record in records:
        service = str(record.get("Service", "")).strip().lower()

        if keyword in service:
            results.append(record)

    return results


def calculate_expense_total(records):
    """計算消費總金額。"""

    total = 0

    for record in records:
        amount = record.get("Amount", 0)

        try:
            total += float(amount)
        except (ValueError, TypeError):
            continue

    return total


def format_expense_result(records, period):
    """將消費查詢結果整理成適合使用者閱讀的文字。"""

    if not records:
        return "📭 目前查不到符合條件的消費資料。"

    total = calculate_expense_total(records)

    lines = [
        "💰 SubWise 消費查詢",
        "",
        f"📅 查詢期間：{period}",
        f"💵 總支出：NT${total:.0f}",
        "",
        "📋 消費明細："
    ]

    for record in records:
        record_date = record.get("Date", "")
        category = record.get("Category", "")
        amount = record.get("Amount", 0)
        note = record.get("Note", "")

        lines.append(
            f"• {record_date}｜{category}｜NT${amount}｜{note}"
        )

    return "\n".join(lines)


def format_subscription_result(records):
    """將訂閱查詢結果整理成適合使用者閱讀的文字。"""

    if not records:
        return "📭 目前沒有找到符合條件的訂閱服務。"

    lines = [
        "🔔 SubWise 訂閱服務",
        ""
    ]

    for record in records:
        service = record.get("Service", "")
        price = record.get("Price", "")
        billing_cycle = record.get("Billing Cycle", "")
        next_date = record.get("Next Billing Date", "")
        status = record.get("Status", "")

        lines.append(f"📌 {service}")
        lines.append(f"💰 費用：NT${price} / {billing_cycle}")
        lines.append(f"📅 下次扣款：{next_date}")
        lines.append(f"🟢 狀態：{status}")
        lines.append("")

    return "\n".join(lines).strip()


def query_data(data):
    """
    根據 Gemini 回傳的 query JSON，
    查詢 Google Sheets 並產生使用者可閱讀的結果。
    """

    target = data.get("target")
    period = data.get("period", "all")
    keyword = data.get("keyword")

    # -------------------------
    # 查詢消費
    # -------------------------

    if target == "expense":

        records = get_expenses()

        records = filter_expenses(
            records,
            period
        )

        return format_expense_result(
            records,
            period
        )

    # -------------------------
    # 查詢訂閱
    # -------------------------

    if target == "subscription":

        records = get_subscriptions()

        records = search_subscriptions(
            records,
            keyword
        )

        return format_subscription_result(
            records
        )

    return "⚠️ 目前無法判斷你想查詢哪一類資料。"