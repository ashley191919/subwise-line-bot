from google_sheets import get_expenses
from query_service import filter_expenses, calculate_expense_total
from datetime import date


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

    top_percentage = 0

    if total > 0:
        top_percentage = (
            top_amount / total * 100
        )

    daily_average = calculate_daily_average(
        total,
        period
    )

    return {
        "period": period,
        "total": total,
        "category_totals": category_totals,
        "category_percentages": category_percentages,
        "top_category": top_category,
        "top_amount": top_amount,
        "top_percentage": top_percentage,
        "daily_average": daily_average,
        "records": records
    }

def format_analysis_result(result):
    """
    將消費分析結果整理成適合 LINE 顯示的文字。
    """

    if not result:
        return "📭 目前沒有可分析的消費資料。"

    period = result.get("period", "month")
    total = result.get("total", 0)
    daily_average = result.get("daily_average", 0)

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

    lines = [
        "📊 SubWise 消費分析",
        "",
        f"📅 分析期間：{period}",
        f"💵 總支出：NT${total:.0f}",
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
        "📂 分類支出："
    ])

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

    if total <= 0 or not top_category:
        return "💡 目前沒有足夠的消費資料可以分析。"

    if top_percentage >= 80:
        return (
            f"💡 消費提醒\n"
            f"{top_category} 類別占本月支出的 "
            f"{top_percentage:.1f}%，"
            f"是目前最主要的消費來源。"
        )

    if top_percentage >= 50:
        return (
            f"💡 消費提醒\n"
            f"{top_category} 類別占本月支出的 "
            f"{top_percentage:.1f}%，"
            f"目前是你的主要支出類別。"
        )

    return (
        f"💡 消費提醒\n"
        f"目前最高支出類別為 {top_category}，"
        f"占本月支出的 {top_percentage:.1f}%。"
    )