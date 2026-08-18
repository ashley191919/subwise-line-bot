from google_sheets import get_expenses
from query_service import filter_expenses, calculate_expense_total
from datetime import date, timedelta


def calculate_category_totals(records):
    """
    計算各消費類別的總金額。
    """

    category_totals = {}

    for record in records:

        category = str(
            record.get("Category", "Other")
        ).strip()

        if not category:
            category = "Other"

        amount = record.get("Amount", 0)

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            continue

        category_totals[category] = (
            category_totals.get(category, 0) + amount
        )

    return category_totals


def calculate_category_percentages(category_totals, total):
    """
    計算各消費類別占總支出的百分比。
    """

    percentages = {}

    if total <= 0:
        return percentages

    for category, amount in category_totals.items():

        percentages[category] = (
            amount / total * 100
        )

    return percentages

def get_top_category(category_totals):
    """
    找出支出最高的消費類別。
    """

    if not category_totals:
        return None, 0

    top_category = max(
        category_totals,
        key=category_totals.get
    )

    top_amount = category_totals[top_category]

    return top_category, top_amount

def get_highest_expense(records):
    """
    找出指定期間內金額最高的單筆消費。
    """

    if not records:
        return None

    highest_expense = None
    highest_amount = 0

    for record in records:

        amount = record.get("Amount", 0)

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            continue

        if amount > highest_amount:

            highest_amount = amount
            highest_expense = record

    return highest_expense

def calculate_daily_average(total, period):
    """
    計算指定期間的平均每日支出。
    """

    if total <= 0:
        return 0

    today = date.today()

    if period == "today":
        days = 1

    elif period == "yesterday":
        days = 1

    elif period == "week":
        days = 7

    elif period == "month":
        days = today.day

    else:
        return 0

    return total / days

def get_previous_month_range():
    """
    取得上個月的開始日期與結束日期。
    """

    today = date.today()

    # 如果現在是 1 月
    if today.month == 1:
        previous_year = today.year - 1
        previous_month = 12

    else:
        previous_year = today.year
        previous_month = today.month - 1

    # 上個月第一天
    start_date = date(
        previous_year,
        previous_month,
        1
    )

    # 本月第一天
    current_month_start = date(
        today.year,
        today.month,
        1
    )

    # 本月第一天往前一天 = 上個月最後一天
    end_date = current_month_start - timedelta(days=1)

    return start_date, end_date

def compare_monthly_expenses():
    """
    比較本月與上個月的消費總額。
    """

    records = get_expenses()

    today = date.today()

    # =========================
    # 本月
    # =========================

    current_month_start = today.replace(day=1)

    current_month_records = []

    for record in records:

        record_date = record.get("Date")

        if not record_date:
            continue

        try:
            record_date = date.fromisoformat(
                str(record_date)
            )
        except ValueError:
            continue

        if current_month_start <= record_date <= today:
            current_month_records.append(record)

    current_total = calculate_expense_total(
        current_month_records
    )

    # =========================
    # 上個月
    # =========================

    previous_month_start, previous_month_end = (
        get_previous_month_range()
    )

    previous_month_records = []

    for record in records:

        record_date = record.get("Date")

        if not record_date:
            continue

        try:
            record_date = date.fromisoformat(
                str(record_date)
            )
        except ValueError:
            continue

        if (
            previous_month_start
            <= record_date
            <= previous_month_end
        ):
            previous_month_records.append(record)

    previous_total = calculate_expense_total(
        previous_month_records
    )

    # =========================
    # 計算差額
    # =========================

    difference = (
        current_total
        - previous_total
    )

    # =========================
    # 計算變化百分比
    # =========================

    if previous_total > 0:

        change_percentage = (
            difference
            / previous_total
            * 100
        )

    else:
        change_percentage = 0

    return {
        "current_month_total": current_total,
        "previous_month_total": previous_total,
        "difference": difference,
        "change_percentage": change_percentage
    }

def get_expense_analysis(period="month"):
    """
    取得指定期間的消費分析資料。
    """

    records = get_expenses()

    records = filter_expenses(
        records,
        period
    )

    total = calculate_expense_total(records)

    category_totals = calculate_category_totals(
        records
    )

    category_percentages = calculate_category_percentages(
        category_totals,
        total
    )

    top_category, top_amount = get_top_category(
        category_totals
    )

    highest_expense = get_highest_expense(
        records
    )

    top_percentage = 0

    if total > 0:
        top_percentage = (
            top_amount / total * 100
        )

    daily_average = calculate_daily_average(
        total,
        period
    )

    expense_count = len(records)

    monthly_comparison = None

    if period == "month":
        monthly_comparison = compare_monthly_expenses()

    return {
        "period": period,
        "total": total,
        "category_totals": category_totals,
        "category_percentages": category_percentages,
        "top_category": top_category,
        "top_amount": top_amount,
        "top_percentage": top_percentage,
        "daily_average": daily_average,
        "expense_count": expense_count,
        "highest_expense": highest_expense,
        "monthly_comparison": monthly_comparison,
        "records": records
    }

def analyze_expenses(data):
    """
    根據 Gemini 回傳的分析 JSON，
    執行消費分析並產生 LINE 回覆。
    """

    period = data.get(
        "period",
        "month"
    )

    print(f"📅 分析期間：{period}")

    result = get_expense_analysis(
        period
    )

    print(f"📊 分析資料：{result}")

    analysis_text = format_analysis_result(
        result
    )

    insight_text = generate_spending_insight(
        result
    )


    return (
        f"{analysis_text}\n\n"
        f"💡 智慧消費提醒\n"
        f"{insight_text}"
    )

def format_analysis_result(result):
    """
    將消費分析結果整理成適合 LINE 顯示的文字。
    """

    if not result:
        return "📭 目前沒有可分析的消費資料。"

    period = result.get("period", "month")
    total = result.get("total", 0)
    daily_average = result.get(
        "daily_average",
        0
    )
    expense_count = result.get(
        "expense_count",
        0
    )

    category_totals = result.get(
        "category_totals",
        {}
    )

    category_percentages = result.get(
        "category_percentages",
        {}
    )

    top_category = result.get(
        "top_category"
    )

    top_amount = result.get(
        "top_amount",
        0
    )

    top_percentage = result.get(
        "top_percentage",
        0
    )

    highest_expense = result.get(
        "highest_expense"
    )

    monthly_comparison = result.get(
        "monthly_comparison"
    )

    lines = [
        "📊 SubWise 消費分析",
        "",
        f"📅 分析期間：{period}",
        f"💵 總支出：NT${total:.0f}",
        f"🧾 消費筆數：{expense_count} 筆",
        f"📊 平均每日：NT${daily_average:.0f}",
        "",
        "🔥 最高支出類別："
    ]

    if top_category:
        lines.append(
            f"• {top_category}："
            f"NT${top_amount:.0f} "
            f"({top_percentage:.1f}%)"
        )
    else:
        lines.append("• 目前沒有消費資料")


    lines.extend([
        "",
        "💳 最高單筆消費："
    ])


    if highest_expense:

        highest_amount = highest_expense.get(
            "Amount",
            0
        )

        highest_category = highest_expense.get(
            "Category",
            "Other"
        )

        highest_note = highest_expense.get(
            "Note",
            ""
        )

        try:
            highest_amount = float(
                highest_amount
            )
        except (ValueError, TypeError):
            highest_amount = 0

        if highest_note:

            lines.append(
                f"• NT${highest_amount:.0f}"
                f"｜{highest_category}"
                f"｜{highest_note}"
            )

        else:

            lines.append(
                f"• NT${highest_amount:.0f}"
                f"｜{highest_category}"
            )

    else:

        lines.append(
            "• 目前沒有消費資料"
        )


    lines.extend([
        "",
        "📂 分類支出："
    ])

    if category_totals:

        for category, amount in category_totals.items():

            percentage = category_percentages.get(
                category,
                0
            )

            lines.append(
                f"• {category}："
                f"NT${amount:.0f} "
                f"({percentage:.1f}%)"
            )

    else:

        lines.append(
            "• 目前沒有消費資料"
        )

    if period == "month" and monthly_comparison:

        comparison_text = format_monthly_comparison(
            monthly_comparison
        )

        lines.extend([
            "",
            comparison_text
        ])

    return "\n".join(lines)

def generate_spending_insight(result):
    """
    根據消費分析結果產生簡單的消費提醒。
    """

    if not result:
        return "💡 目前沒有足夠的消費資料可以分析。"

    total = result.get("total", 0)
    top_category = result.get("top_category")
    top_percentage = result.get("top_percentage", 0)
    period = result.get("period", "month")

    if period == "today":
        period_text = "今天"

    elif period == "yesterday":
        period_text = "昨天"

    elif period == "week":
        period_text = "本週"

    elif period == "month":
        period_text = "本月"

    else:
        period_text = "目前期間"

    if total <= 0 or not top_category:
        return "💡 目前沒有足夠的消費資料可以分析。"

    if top_percentage >= 80:
        return (
            f"{top_category} 類別占{period_text}支出的 "
            f"{top_percentage:.1f}%，"
            f"是目前最主要的消費來源。"
        )

    if top_percentage >= 50:
        return (
            f"{top_category} 類別占{period_text}支出的 "
            f"{top_percentage:.1f}%，"
            f"目前是你的主要支出類別。"
        )

    return (
        f"目前最高支出類別為 {top_category}，"
        f"占{period_text}支出的 {top_percentage:.1f}%。"
    )

def format_monthly_comparison(result):
    """
    將本月與上月消費比較結果整理成 LINE 可閱讀的文字。
    """

    if not result:
        return "📭 目前沒有足夠的資料可以進行月份比較。"

    current_total = result.get(
        "current_month_total",
        0
    )

    previous_total = result.get(
        "previous_month_total",
        0
    )

    difference = result.get(
        "difference",
        0
    )

    change_percentage = result.get(
        "change_percentage",
        0
    )

    lines = [
        "📊 SubWise 月度比較",
        "",
        f"📅 本月支出：NT${current_total:.0f}"
    ]

    # =========================
    # 上月沒有資料
    # =========================

    if previous_total <= 0:

        lines.extend([
            "📅 上月支出：目前沒有資料",
            "",
            f"💡 本月已累計 NT${current_total:.0f}，",
            "目前尚無法與上月進行完整比較。"
        ])

        return "\n".join(lines)

    # =========================
    # 上月有資料
    # =========================

    lines.extend([
        f"📅 上月支出：NT${previous_total:.0f}",
        ""
    ])

    if difference > 0:

        lines.append(
            f"📈 比上月增加：NT${difference:.0f}"
        )

        lines.append(
            f"📊 變化幅度：+{change_percentage:.1f}%"
        )

        lines.extend([
            "",
            (
                f"💡 本月支出比上月增加 "
                f"{change_percentage:.1f}%。"
            )
        ])

    elif difference < 0:

        lines.append(
            f"📉 比上月減少：NT${abs(difference):.0f}"
        )

        lines.append(
            f"📊 變化幅度：{change_percentage:.1f}%"
        )

        lines.extend([
            "",
            (
                f"💡 本月支出比上月下降 "
                f"{abs(change_percentage):.1f}%。"
            )
        ])

    else:

        lines.extend([
            "➡️ 與上月支出相同",
            "📊 變化幅度：0.0%"
        ])

    return "\n".join(lines)