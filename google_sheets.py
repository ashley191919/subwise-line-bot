import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_worksheet(sheet_name="Expenses"):
    """取得指定的 Google Sheets 工作表。"""

    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
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