"""Order history manager for KFC campus ordering assistant.

Stores order history as JSON in the skill's assets directory.

Usage:
  python history_manager.py add '<json-order>'
  python history_manager.py list [--limit N]
  python history_manager.py get <order-id>
  python history_manager.py delete <order-id>
  python history_manager.py clear
"""

import json
import os
import sys
import uuid
from datetime import datetime

HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "order_history.json"
)


def _load():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save(orders):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


def add_order(order_data):
    """Add a new order to history."""
    if isinstance(order_data, str):
        order_data = json.loads(order_data)

    orders = _load()
    order_data["id"] = uuid.uuid4().hex[:8]
    order_data["created_at"] = datetime.now().isoformat()
    orders.append(order_data)
    _save(orders)
    print(json.dumps(order_data, ensure_ascii=False, indent=2))


def list_orders(limit=10):
    """List recent orders."""
    orders = _load()
    recent = sorted(orders, key=lambda o: o.get("created_at", ""), reverse=True)[:limit]

    if not recent:
        print("暂无历史订单")
        return

    print(f"{'订单ID':<10} {'日期':<12} {'内容':<30} {'金额':>8}")
    print("-" * 65)
    for o in recent:
        oid = o.get("id", "")
        date = o.get("created_at", "")[:10]
        items = ", ".join(
            f"{i.get('name','')}x{i.get('qty',1)}" for i in o.get("items", [])
        )
        if len(items) > 28:
            items = items[:27] + "…"
        total = o.get("final", o.get("total", 0))
        print(f"{oid:<10} {date:<12} {items:<30} ¥{total:>7.2f}")


def get_order(order_id):
    """Get a specific order by ID."""
    orders = _load()
    for o in orders:
        if o.get("id") == order_id:
            print(json.dumps(o, ensure_ascii=False, indent=2))
            return
    print(f"订单 {order_id} 不存在")


def delete_order(order_id):
    """Delete an order by ID."""
    orders = _load()
    filtered = [o for o in orders if o.get("id") != order_id]
    if len(filtered) == len(orders):
        print(f"订单 {order_id} 不存在")
        return
    _save(filtered)
    print(f"订单 {order_id} 已删除")


def clear_all():
    """Clear all order history."""
    _save([])
    print("所有订单记录已清除")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: history_manager.py <add|list|get|delete|clear> [args...]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        if len(sys.argv) < 3:
            data = json.load(sys.stdin)
        else:
            data = sys.argv[2]
        add_order(data)
    elif cmd == "list":
        limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--limit" else 10
        list_orders(limit)
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: history_manager.py get <order-id>")
            sys.exit(1)
        get_order(sys.argv[2])
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Usage: history_manager.py delete <order-id>")
            sys.exit(1)
        delete_order(sys.argv[2])
    elif cmd == "clear":
        clear_all()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
