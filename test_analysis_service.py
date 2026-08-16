from analysis_service import (
    get_expense_analysis,
    format_analysis_result,
    generate_spending_insight
)


print("🧪 SubWise Analysis Service 測試")
print("=" * 50)

print("\n📊 開始分析本月消費...")

result = get_expense_analysis("month")

print("\n📌 分析結果：")

print(f"📅 分析期間：{result['period']}")
print(f"💵 總支出：NT${result['total']:.0f}")

print("\n📂 分類統計：")

for category, amount in result["category_totals"].items():

    percentage = result["category_percentages"].get(
        category,
        0
    )

    print(
        f"• {category}："
        f"NT${amount:.0f} "
        f"({percentage:.1f}%)"
    )

print("\n🔥 最高支出類別：")

print(
    f"• {result['top_category']}："
    f"NT${result['top_amount']:.0f} "
    f"({result['top_percentage']:.1f}%)"
)

print("\n📊 平均每日支出：")

print(
    f"• 約 NT${result['daily_average']:.0f} / 天"
)


print("\n📱 LINE 分析結果：")
print("-" * 50)

message = format_analysis_result(result)

print(message)

print("\n💡 智慧消費提醒：")
print("-" * 50)

insight = generate_spending_insight(result)

print(insight)

print("\n✅ Analysis Service 測試完成")