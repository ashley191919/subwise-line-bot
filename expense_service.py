from google_sheets import add_expense


def save_expense(data):
    """
    將 Gemini 回傳的 expense JSON
    驗證後寫入 Google Sheets。
    """

    if not data:
        print("❌ 沒有收到資料")
        return False

    # 確認資料類型
    if data.get("type") != "expense":
        print("❌ 資料類型不是 expense")
        return False

    amount = data.get("amount")
    category = data.get("category")
    item = data.get("item")
    expense_date = data.get("date")
    note = data.get("note")

    # =========================
    # 1. 檢查必要欄位
    # =========================

    if amount is None:
        print("❌ 缺少消費金額")
        return False

    if expense_date is None:
        print("❌ 缺少消費日期")
        return False

    if category is None:
        print("⚠️ 缺少消費分類，將使用 Other")
        category = "Other"

    # =========================
    # 2. 檢查金額格式
    # =========================

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        print("❌ 消費金額格式錯誤")
        return False

    # 不允許 0 或負數
    if amount <= 0:
        print("❌ 消費金額必須大於 0")
        return False

    # 如果是整數，就不要存成 120.0
    if amount.is_integer():
        amount = int(amount)

    # =========================
    # 3. 合併 item 與 note
    # =========================

    if item and note:
        final_note = f"{item}｜{note}"
    elif item:
        final_note = item
    elif note:
        final_note = note
    else:
        final_note = ""

    # =========================
    # 4. 寫入 Google Sheets
    # =========================

    try:
        add_expense(
            expense_date,
            category,
            amount,
            final_note
        )

        print("✅ 消費資料已寫入 Google Sheets")
        return True

    except Exception as e:
        print(f"❌ Google Sheets 寫入失敗：{e}")
        return False