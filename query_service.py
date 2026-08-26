from datetime import date, timedelta
CATEGORY_DISPLAY_NAMES = {
    "Food": "🍜 餐飲",
    "Transport": "🚇 交通",
    "Entertainment": "🎮 娛樂",
    "Shopping": "🛍️ 購物",
    "Bills": "💡 生活帳單",
    "Health": "❤️ 醫療保健",
    "Education": "📚 學習",
    "Subscription": "🔔 訂閱",
    "Other": "📦 其他"
}

from google_sheets import (
    get_expenses,
    get_subscriptions,
    get_expenses_with_rows,
    update_expense_row,
    delete_expense
)

def get_upcoming_subscriptions(records, days=7):
    """
    找出未來指定天數內即將扣款的 Active 訂閱。

    例如今天是 2026-08-26、days=7，
    就會找出 2026-08-27 ～ 2026-09-02
    之間且狀態為 Active 的訂閱。
    """

    today = date.today()
    end_date = today + timedelta(days=days)

    upcoming = []

    for record in records:

        status = str(
            record.get("Status", "")
        ).strip().lower()

        # 只提醒啟用中的訂閱
        if status != "active":
            continue

        next_billing_date = record.get(
            "Next Billing Date"
        )

        if not next_billing_date:
            continue

        try:
            billing_date = date.fromisoformat(
                str(next_billing_date).strip()
            )
        except ValueError:
            continue

        if today < billing_date <= end_date:

            days_until = (
                billing_date - today
            ).days

            subscription = record.copy()

            subscription["days_until"] = days_until

            upcoming.append(subscription)

    upcoming.sort(
        key=lambda record: record.get(
            "Next Billing Date",
            ""
        )
    )

    return upcoming

def format_upcoming_subscriptions(records):
    """
    將即將扣款的訂閱資料整理成適合 LINE 顯示的文字。
    """

    if not records:
        return "🔔 最近 7 天沒有即將扣款的訂閱。"

    lines = [
        "⏰ 即將扣款提醒",
        ""
    ]

    for record in records:
        service = record.get("Service", "")
        price = record.get("Price", "")
        next_date = record.get("Next Billing Date", "")
        days_until = record.get("days_until")

        if days_until == 0:
            timing = "⚠️ 今天扣款"
        elif days_until == 1:
            timing = "🔔 明天扣款"
        else:
            timing = f"📅 {days_until} 天後扣款"

        lines.append(
            f"📌 {service}"
        )
        lines.append(
            f"💰 費用：NT${price}"
        )
        lines.append(
            f"📅 扣款日：{next_date}"
        )
        lines.append(
            timing
        )
        lines.append("")

    return "\n".join(lines).strip()

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

    elif period == "all":
        return records

    else:
        return []

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

def sort_expenses_by_date(records):
    """
    將消費資料按照日期由新到舊排序。
    """

    return sorted(
        records,
        key=lambda record: str(
            record.get("Date", "")
        ),
        reverse=True
    )

def find_latest_expense_with_row():
    """
    找出 Google Sheets 中最後一筆消費。
    """

    records = get_expenses_with_rows()

    if not records:
        return None

    return records[-1]


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

def filter_expenses_by_category(records, category=None):
    """
    根據消費分類篩選資料。
    """

    if not category:
        return records

    filtered = []

    for record in records:

        record_category = str(
            record.get("Category", "")
        ).strip()

        if record_category == category:
            filtered.append(record)

    return filtered

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

def find_highest_expense(records):
    """
    找出消費資料中金額最高的一筆。
    """

    if not records:
        return None

    highest = None

    for record in records:

        amount = record.get("Amount", 0)

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            continue

        if highest is None:
            highest = record
            continue

        highest_amount = highest.get("Amount", 0)

        try:
            highest_amount = float(highest_amount)
        except (ValueError, TypeError):
            continue

        if amount > highest_amount:
            highest = record

    return highest


def format_expense_result(records, period):
    """將消費查詢結果整理成適合使用者閱讀的文字。"""

    if not records:
        return "📭 目前查不到符合條件的消費資料。"

    # 1. 計算總支出
    total = calculate_expense_total(records)

    # 2. 計算消費筆數
    count = len(records)

    # 3. 找出最高單筆消費
    highest = find_highest_expense(records)

    # 4. 將消費按照日期由新到舊排序
    records = sort_expenses_by_date(records)

    lines = [
        "💰 SubWise 消費查詢",
        "",
        f"📅 查詢期間：{period}",
        f"💵 總支出：NT${total:.0f}",
        f"🧾 消費筆數：{count} 筆",
    ]

    # 5. 顯示最高單筆消費
    if highest:

        highest_date = highest.get(
            "Date",
            ""
        )

        highest_amount = highest.get(
            "Amount",
            0
        )

        highest_category = highest.get(
            "Category",
            ""
        )

        highest_category_display = CATEGORY_DISPLAY_NAMES.get(
            highest_category,
            highest_category
        )

        highest_note = highest.get(
            "Note",
            ""
        )

        lines.extend([
            "",
            "🔥 最高單筆消費",
            f"📅 日期：{highest_date}",
            f"💵 金額：NT${float(highest_amount):.0f}",
            f"📂 分類：{highest_category_display}",
            f"📝 備註：{highest_note}"
        ])

    # 6. 顯示消費明細
    lines.extend([
        "",
        "📋 最近消費："
    ])

    for record in records:

        record_date = record.get(
            "Date",
            ""
        )

        category = record.get(
            "Category",
            ""
        )
        
        category_display = CATEGORY_DISPLAY_NAMES.get(
            category,
            category
        )

        amount = record.get(
            "Amount",
            0
        )

        note = record.get(
            "Note",
            ""
        )

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0

        lines.append(
            f"• {record_date}｜"
            f"{category_display}｜"
            f"NT${amount:.0f}｜"
            f"{note}"
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
    category = data.get("category")
    upcoming = data.get("upcoming", False)

    # -------------------------
    # 查詢消費
    # -------------------------

    if target == "expense":

        records = get_expenses()

        records = filter_expenses(
            records,
            period
        )

        records = filter_expenses_by_category(
            records,
            category
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

        # -------------------------
        # 即將扣款查詢
        # -------------------------

        if upcoming:

            records = get_upcoming_subscriptions(
                records,
                days=7
            )

            return format_upcoming_subscriptions(
                records
            )

        # -------------------------
        # 一般訂閱查詢
        # -------------------------

        records = filter_subscriptions_by_period(
            records,
            period
        )

        records = search_subscriptions(
            records,
            keyword
        )

        return format_subscription_result(
            records
        )

    return "⚠️ 目前無法判斷你想查詢哪一類資料。"

def filter_subscriptions_by_period(records, period="all"):
    """依照下次扣款日期篩選訂閱資料。"""

    today = date.today()

    if period == "today":
        start_date = today
        end_date = today

    elif period == "yesterday":
        yesterday = today - timedelta(days=1)
        start_date = yesterday
        end_date = yesterday

    elif period == "week":
        start_date = today
        end_date = today + timedelta(days=6)

    elif period == "month":
        start_date = today.replace(day=1)

        if today.month == 12:
            next_month = today.replace(
                year=today.year + 1,
                month=1,
                day=1
            )
        else:
            next_month = today.replace(
                month=today.month + 1,
                day=1
            )

        end_date = next_month - timedelta(days=1)

    elif period == "all":
        return records

    else:
        return []

    filtered = []

    for record in records:

        next_date = record.get(
            "Next Billing Date"
        )

        if not next_date:
            continue

        try:
            next_date = date.fromisoformat(
                str(next_date)
            )
        except ValueError:
            continue

        if start_date <= next_date <= end_date:
            filtered.append(record)

    return filtered