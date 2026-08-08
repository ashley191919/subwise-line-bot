import gspread
from google.oauth2.service_account import Credentials
from datetime import date

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

# 測試資料
data = [
    str(date.today()),
    "Food",
    120,
    "Lunch"
]

# 寫入下一個空白列
worksheet.append_row(data)

print("🎉 Google Sheets 寫入成功！")
print("📄 試算表：", spreadsheet.title)
print("📚 工作表：", worksheet.title)
print("📝 寫入資料：")
print(f"   日期：{data[0]}")
print(f"   類別：{data[1]}")
print(f"   金額：{data[2]}")
print(f"   備註：{data[3]}")