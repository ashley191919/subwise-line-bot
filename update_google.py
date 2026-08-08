import gspread
from google.oauth2.service_account import Credentials

# Google API 權限
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 使用 Service Account 憑證
credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

# 登入 Google Sheets
client = gspread.authorize(credentials)

# 開啟 SubWise Database
spreadsheet = client.open("SubWise Database")

# 取得 Expenses 工作表
worksheet = spreadsheet.worksheet("Expenses")

# 修改第一筆資料的金額
worksheet.update_cell(2, 3, 150)

print("✏️ 資料修改成功！")
print("📄 工作表：Expenses")
print("💰 第一筆消費金額：120 → 150")