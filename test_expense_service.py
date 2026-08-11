import gspread
from google.oauth2.service_account import Credentials

from gemini_client import ask_gemini


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_worksheet(sheet_name):
    """取得指定的 Google Sheets 工作表。"""
    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES,
    )
    client = gspread.authorize(credentials)
    spreadsheet = client.open("SubWise Database")

    return spreadsheet.worksheet(sheet_name)


def add_expense(data):
    """新增或更新消費資料。"""
    if data.get("category") is None:
        print("⚠️ 缺少消費分類")
        return False

    if data.get("amount") is None:
        print("⚠️ 缺少消費金額")
        return False

    worksheet = get_worksheet("Expenses")
    worksheet.append_row([
        data.get("date"),
        data.get("category"),
        data.get("amount"),
        data.get("item"),
        data.get("note"),
    ])

    print("✅ 消費資料已寫入 Google Sheets")
    return True


def add_subscription(data):
    """新增或更新訂閱資料。"""

    name = data.get("name")
    amount = data.get("amount")
    billing_cycle = data.get("billing_cycle")
    next_billing_date = data.get("next_billing_date")
    category = data.get("category")
    note = data.get("note")

    # 檢查必要欄位
    if name is None:
        print("⚠️ 缺少訂閱名稱")
        return False

    if amount is None:
        print("⚠️ 缺少訂閱金額")
        return False

    # 取得 Subscriptions 工作表
    worksheet = get_worksheet("Subscriptions")

    # 取得目前所有訂閱資料
    records = worksheet.get_all_records()

    # 檢查是否已經存在相同訂閱
    for row_number, record in enumerate(records, start=2):

        existing_name = str(
            record.get("Service", "")
        ).strip()

        if existing_name.lower() == str(name).strip().lower():

            print(f"🔄 發現既有訂閱：{name}")

            # 更新既有訂閱
            worksheet.update(
                range_name=f"A{row_number}:G{row_number}",
                values=[[
                    name,
                    amount,
                    billing_cycle,
                    next_billing_date,
                    "Active",
                    category,
                    note
                ]]
            )

            print(f"✅ 已更新第 {row_number} 列資料")
            return True

    # 找不到相同訂閱 → 新增一筆
    worksheet.append_row([
        name,
        amount,
        billing_cycle,
        next_billing_date,
        "Active",
        category,
        note,
    ])

    print("✅ 訂閱資料已寫入 Google Sheets")
    return True


def show_result(data):
    """顯示 Gemini 判斷結果。"""
    print("\n📦 Gemini JSON：")
    print(data)

    if data is None:
        print("❌ Gemini 沒有回傳有效資料")
        return

    data_type = data.get("type")

    if data_type == "expense":
        print("\n📌 Python 已成功解析：")
        print(f"類型：{data.get('type')}")
        print(f"分類：{data.get('category')}")
        print(f"金額：{data.get('amount')}")
        print(f"項目：{data.get('item')}")
        print(f"日期：{data.get('date')}")
        print(f"備註：{data.get('note')}")

    elif data_type == "subscription":
        print("\n📌 Python 已成功解析：")
        print(f"類型：{data.get('type')}")
        print(f"服務：{data.get('name')}")
        print(f"金額：{data.get('amount')}")
        print(f"扣款週期：{data.get('billing_cycle')}")
        print(f"下次扣款：{data.get('next_billing_date')}")
        print(f"分類：{data.get('category')}")
        print(f"備註：{data.get('note')}")

    elif data_type == "chat":
        print("\n📌 Python 已成功解析：")
        print(f"類型：{data.get('type')}")
        print(f"AI 回覆：{data.get('message')}")

    else:
        print(f"⚠️ 未知的資料類型：{data_type}")


print("🚀 SubWise AI → Google Sheets 測試")
print("=" * 50)

while True:
    prompt = input("\n你：")

    if prompt.lower() in ["exit", "quit"]:
        print("👋 測試結束！")
        break

    if not prompt.strip():
        print("⚠️ 請輸入內容。")
        continue

    print("\n🤖 Gemini 思考中...")
    data = ask_gemini(prompt)
    show_result(data)

    if data is None:
        print("❌ 無法取得 Gemini 資料")
        continue

    data_type = data.get("type")

    if data_type == "expense":
        print("\n💾 嘗試寫入 Google Sheets...")
        success = add_expense(data)

        if success:
            print("🎉 記帳完成！")
        else:
            print("⚠️ 記帳失敗，資料沒有寫入。")

    elif data_type == "subscription":
        print("\n🔔 偵測到訂閱資料")
        print("💾 嘗試寫入 Google Sheets...")
        success = add_subscription(data)

        if success:
            print("🎉 訂閱建立完成！")
        else:
            print("⚠️ 訂閱建立失敗，資料沒有寫入。")

    elif data_type == "chat":
        print("\n💬 一般對話，不寫入 Google Sheets。")
        print(f"🤖 SubWise：{data.get('message')}")

    else:
        print("⚠️ 無法判斷資料類型。")
