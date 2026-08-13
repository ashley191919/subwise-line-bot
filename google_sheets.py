import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, timedelta


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_worksheet(sheet_name="Expenses"):
    """取得指定的 Google Sheets 工作表。"""

    if os.getenv("GOOGLE_CREDENTIALS_JSON"):
        credentials_info = json.loads(
            os.getenv("GOOGLE_CREDENTIALS_JSON")
        )

        credentials = Credentials.from_service_account_info(
            credentials_info,
            scopes=SCOPES,
        )
    else:
        credentials = Credentials.from_service_account_file(
            "credentials.json",
            scopes=SCOPES,
        )

    client = gspread.authorize(credentials)

    spreadsheet = client.open("SubWise Database")

    return spreadsheet.worksheet(sheet_name)


def add_expense(date, category, amount, note):
    """新增一筆消費資料。"""

    worksheet = get_worksheet()

    worksheet.append_row([
        date,
        category,
        amount,
        note
    ])

    return True


def get_expenses():
    """取得所有消費資料。"""

    worksheet = get_worksheet()

    return worksheet.get_all_records()


def update_expense(row, column, value):
    """修改指定儲存格。"""

    worksheet = get_worksheet()

    worksheet.update_cell(row, column, value)

    return True


def delete_expense(row):
    """刪除指定資料列。"""

    worksheet = get_worksheet()

    worksheet.delete_rows(row)

    return True

def get_subscriptions():
    """取得所有訂閱資料。"""

    worksheet = get_worksheet("Subscriptions")

    return worksheet.get_all_records()

def query_data(target):
    """
    根據查詢目標取得資料。
    
    target:
        expense → 消費資料
        subscription → 訂閱資料
    """

    if target == "expense":
        return get_expenses()

    elif target == "subscription":
        return get_subscriptions()

    else:
        print(f"⚠️ 不支援的查詢目標：{target}")
        return []

def filter_expenses_by_period(expenses, period):
    """
    根據 period 篩選消費資料。

    period:
        today
        yesterday
        week
        month
        all
    """

    if period == "all":
        return expenses

    today = date.today()

    if period == "today":
        start_date = today
        end_date = today

    elif period == "yesterday":
        start_date = today - timedelta(days=1)
        end_date = start_date

    elif period == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = today

    elif period == "month":
        start_date = today.replace(day=1)
        end_date = today

    else:
        print(f"⚠️ 不支援的查詢期間：{period}")
        return []

    filtered = []

    for expense in expenses:

        expense_date = expense.get("Date")

        if not expense_date:
            continue

        try:
            expense_date = date.fromisoformat(str(expense_date))
        except ValueError:
            continue

        if start_date <= expense_date <= end_date:
            filtered.append(expense)

    return filtered

def filter_subscriptions_by_keyword(subscriptions, keyword):
    """
    根據訂閱服務名稱搜尋資料。
    """

    if not keyword:
        return subscriptions

    keyword = str(keyword).strip().lower()

    filtered = []

    for subscription in subscriptions:

        service = str(
            subscription.get("Service", "")
        ).strip().lower()

        if keyword in service:
            filtered.append(subscription)

    return filtered