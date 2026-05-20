"""KFC menu data helper for campus ordering assistant.

School-cafe-specific: limited menu, 大神卡 (VIP) discounts, no campus card 9% off.
Uses KFC APP for ordering, pickup/takeaway only.

Usage:
  python fetch_menu.py parse <json-file>       Parse menu JSON and display formatted
  python fetch_menu.py compare <item1> <item2>  Compare two items/combos
  python fetch_menu.py calc <json-order>        Calculate total with discounts
"""

import json
import sys
import os

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
)


def format_price(price):
    return f"¥{price:.2f}"


def parse_menu(data):
    """Parse and display menu data with VIP prices if available."""
    if isinstance(data, str):
        data = json.loads(data)

    output = []
    categories = data.get("categories", {})
    for cat_name, items in categories.items():
        output.append(f"\n## {cat_name}")
        output.append(f"{'餐品名称':<22} {'原价':>8} {'大神卡价':>8}")
        output.append("-" * 48)
        for item in items:
            name = item.get("name", "")
            price = item.get("price", 0)
            vip_price = item.get("vip_price", price)
            limited = " ⚠" if item.get("campus_limited", False) else ""
            output.append(
                f"{name + limited:<22} {format_price(price):>8}"
                f" {format_price(vip_price):>8}"
            )
    return "\n".join(output)


def calculate_order(order_data):
    """Calculate order total with combo and VIP discounts."""
    if isinstance(order_data, str):
        order_data = json.loads(order_data)

    items = order_data.get("items", [])
    subtotal_original = sum(
        item.get("price", 0) * item.get("qty", 1) for item in items
    )
    subtotal_vip = sum(
        item.get("vip_price", item.get("price", 0)) * item.get("qty", 1)
        for item in items
    )
    combo_discount = order_data.get("combo_discount", 0)
    vip_discount = subtotal_original - subtotal_vip
    after_combo = subtotal_vip - combo_discount
    final = max(after_combo, 0)

    result = {
        "subtotal_original": round(subtotal_original, 2),
        "subtotal_vip": round(subtotal_vip, 2),
        "combo_discount": combo_discount,
        "vip_discount": round(vip_discount, 2),
        "final": round(final, 2),
        "savings": round(subtotal_original - final, 2),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def compare_items(item1, item2):
    """Compare two menu items or combos."""
    if isinstance(item1, str):
        item1 = json.loads(item1)
    if isinstance(item2, str):
        item2 = json.loads(item2)

    def effective_price(item):
        return item.get("vip_price", item.get("price", 0))

    price1 = effective_price(item1)
    price2 = effective_price(item2)
    diff = price1 - price2

    lines = [
        "对比 (含大神卡优惠):",
        f"  {item1.get('name', 'Item1')}: {format_price(price1)}",
        f"  {item2.get('name', 'Item2')}: {format_price(price2)}",
        f"  差价: {format_price(abs(diff))}"
        f" ({'方案1更贵' if diff > 0 else '方案2更贵' if diff < 0 else '价格相同'})",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fetch_menu.py <parse|compare|calc> [args...]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "parse":
        data = (
            json.loads(sys.argv[2])
            if len(sys.argv) > 2
            else json.load(sys.stdin)
        )
        print(parse_menu(data))
    elif cmd == "compare":
        if len(sys.argv) < 4:
            print("Usage: fetch_menu.py compare '<json1>' '<json2>'")
            sys.exit(1)
        print(compare_items(sys.argv[2], sys.argv[3]))
    elif cmd == "calc":
        data = (
            json.loads(sys.argv[2])
            if len(sys.argv) > 2
            else json.load(sys.stdin)
        )
        print(calculate_order(data))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
