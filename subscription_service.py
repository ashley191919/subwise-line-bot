from google_sheets import get_worksheet


def save_subscription(data):
    """
    新增或更新一筆訂閱資料。
    如果服務名稱已存在，就更新原本資料。
    """

    if not data:
        print("❌ 沒有收到訂閱資料")
        return False

    if data.get("type") != "subscription":
        print("❌ 資料類型不是 subscription")
        return False

    name = data.get("name")
    amount = data.get("amount")
    billing_cycle = data.get("billing_cycle")
    next_billing_date = data.get("next_billing_date")

    # =========================
    # 1. 檢查必要欄位
    # =========================

    if not name:
        print("⚠️ 缺少訂閱服務名稱")
        return False

    if amount is None:
        print("⚠️ 缺少訂閱金額")
        return False

    if not billing_cycle:
        print("⚠️ 缺少扣款週期")
        return False

    if not next_billing_date:
        print("⚠️ 缺少下次扣款日期")
        return False

    # =========================
    # 2. 檢查金額格式
    # =========================

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        print("❌ 訂閱金額格式錯誤")
        return False

    if amount <= 0:
        print("❌ 訂閱金額必須大於 0")
        return False

    if amount.is_integer():
        amount = int(amount)

    # =========================
    # 3. 取得 Subscriptions 工作表
    # =========================

    try:
        worksheet = get_worksheet("Subscriptions")

        records = worksheet.get_all_records()

        # =========================
        # 4. 搜尋是否已經存在
        # =========================

        existing_row = None

        for index, record in enumerate(records, start=2):

            service_name = str(record.get("Service", "")).strip()

            if service_name.lower() == name.strip().lower():
                existing_row = index
                break

        # =========================
        # 5. 已存在 → 更新
        # =========================

        if existing_row:

            worksheet.update(
                f"A{existing_row}:E{existing_row}",
                [[
                    name,
                    amount,
                    billing_cycle,
                    next_billing_date,
                    "Active"
                ]]
            )

            print(f"🔄 發現既有訂閱：{name}")
            print(f"✅ 已更新第 {existing_row} 列資料")

            return True

        # =========================
        # 6. 不存在 → 新增
        # =========================

        worksheet.append_row([
            name,
            amount,
            billing_cycle,
            next_billing_date,
            "Active"
        ])

        print(f"🆕 新增訂閱：{name}")
        print("✅ 訂閱資料已寫入 Google Sheets")

        return True

    except Exception as e:

        print(f"❌ Google Sheets 操作失敗：{e}")

        return False

def get_subscriptions():
    """
    取得所有訂閱資料。
    """

    try:
        worksheet = get_worksheet("Subscriptions")

        records = worksheet.get_all_records()

        return records

    except Exception as e:

        print(f"❌ 取得訂閱資料失敗：{e}")

        return []

def format_subscriptions(records):
    """
    將訂閱資料整理成使用者容易閱讀的文字。
    """

    if not records:
        return "📋 目前沒有任何訂閱資料。"

    message = "📋 你的訂閱服務\n\n"

    for record in records:

        service = record.get("Service", "未命名")
        price = record.get("Price", 0)
        billing_cycle = record.get("Billing Cycle", "未知")
        next_date = record.get("Next Billing Date", "未知")
        status = record.get("Status", "未知")

        message += (
            f"🔹 {service}\n"
            f"💰 NT${price} / {billing_cycle}\n"
            f"📅 下次扣款：{next_date}\n"
            f"🟢 狀態：{status}\n\n"
        )

    return message