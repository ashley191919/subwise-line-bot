import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet = client.open("SubWise Database")

print("=" * 40)
print("🎉 Google Sheets 連線成功！")
print("=" * 40)

print(f"📄 試算表名稱：{sheet.title}")

worksheets = sheet.worksheets()

print(f"📚 工作表數量：{len(worksheets)}")

print("\n📚 目前工作表：")

for index, ws in enumerate(worksheets, start=1):
    print(f"{index}. {ws.title}")

print("\n🎯 Day06：Google Sheets 環境驗證完成！")