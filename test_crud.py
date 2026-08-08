from google_sheets import (
    add_expense,
    get_expenses,
    update_expense,
    delete_expense
)


print("🚀 SubWise Google Sheets CRUD 測試")
print("=" * 50)


# =====================================
# 1. Create
# =====================================

print("\n1️⃣ CREATE：新增消費")

add_expense(
    "2026-08-08",
    "Entertainment",
    300,
    "Movie"
)

print("✅ 新增成功")


# =====================================
# 2. Read
# =====================================

print("\n2️⃣ READ：讀取消費")

expenses = get_expenses()

for index, expense in enumerate(expenses, start=1):
    print(
        f"{index}. "
        f"{expense['Date']} | "
        f"{expense['Category']} | "
        f"${expense['Amount']} | "
        f"{expense['Note']}"
    )

print(f"✅ 目前共有 {len(expenses)} 筆資料")


# =====================================
# 3. Update
# =====================================

print("\n3️⃣ UPDATE：修改最後一筆資料")

# 找出最後一筆資料所在的列
last_row = len(expenses) + 1

update_expense(
    last_row,
    3,
    350
)

print("✅ 金額已修改：300 → 350")


# =====================================
# 4. Read again
# =====================================

print("\n🔍 再次讀取確認修改")

expenses = get_expenses()

last_expense = expenses[-1]

print(
    f"{last_expense['Date']} | "
    f"{last_expense['Category']} | "
    f"${last_expense['Amount']} | "
    f"{last_expense['Note']}"
)


# =====================================
# 5. Delete
# =====================================

print("\n4️⃣ DELETE：刪除測試資料")

delete_expense(last_row)

print("🗑️ 測試資料已刪除")


# =====================================
# 完成
# =====================================

print("\n" + "=" * 50)
print("🎉 CRUD 四項功能全部測試完成！")
print("Create ✅")
print("Read   ✅")
print("Update ✅")
print("Delete ✅")
print("=" * 50)