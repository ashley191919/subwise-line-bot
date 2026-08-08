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

# 取得所有資料
records = worksheet.get_all_records()

print("📊 SubWise 消費紀錄")
print("=" * 40)

for record in records:
    print(
        f"📅 {record['Date']} | "
        f"🏷️ {record['Category']} | "
        f"💰 ${record['Amount']} | "
        f"📝 {record['Note']}"
    )

print("=" * 40)
print(f"🎯 共讀取 {len(records)} 筆資料")