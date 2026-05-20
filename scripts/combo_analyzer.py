"""KFC combo discount strength analyzer.

Compares combo price against sum of individual item prices to measure
real savings. Used by the recommendation engine to surface the best deals.

Usage:
  python combo_analyzer.py analyze '<combo-json>'
  python combo_analyzer.py rank '<json-array-of-combos>'
  python combo_analyzer.py analyze '<combo-json>' --json
"""

import json
import sys
import os
from typing import TypedDict


class Item(TypedDict):
    name: str
    single_price: float


class Combo(TypedDict):
    name: str
    combo_price: float
    items: list[Item]


def _individual_total(items: list[dict]) -> float:
    return sum(item.get("single_price", 0) for item in items)


def _discount_pct(savings: float, individual_total: float) -> float:
    if individual_total <= 0:
        return 0.0
    return round(savings / individual_total * 100, 1)


def _rating(pct: float) -> str:
    if pct >= 35:
        return "💎 超值"
    if pct >= 20:
        return "👍 很划算"
    if pct >= 10:
        return "✅ 划算"
    if pct >= 0:
        return "➖ 一般"
    return "⚠️ 不划算（套餐价比单品还贵）"


def analyze(combo: dict) -> dict:
    """Analyze discount strength of a single combo."""
    items = combo.get("items", [])
    combo_price = combo.get("combo_price", 0)
    individual_total = _individual_total(items)
    savings = round(individual_total - combo_price, 2)
    pct = _discount_pct(savings, individual_total)

    return {
        "name": combo.get("name", "未命名套餐"),
        "combo_price": combo_price,
        "individual_total": round(individual_total, 2),
        "savings": savings,
        "discount_pct": pct,
        "rating": _rating(pct),
        "items": items,
    }


def format_result(r: dict) -> str:
    lines = [
        f"套餐: {r['name']}",
        f"套餐价: ¥{r['combo_price']:.2f}",
        "",
        "单品拆解:",
    ]
    for item in r["items"]:
        name = item.get("name", "")
        sp = item.get("single_price", 0)
        lines.append(f"  {name:<18} ¥{sp:.2f}")
    lines += [
        f"  {'─' * 26}",
        f"  {'单品合计':<18} ¥{r['individual_total']:.2f}",
        "",
        f"节省: ¥{r['savings']:.2f}  |  优惠力度: {r['discount_pct']}%",
        f"评级: {r['rating']}",
    ]
    return "\n".join(lines)


def rank(combos: list[dict]) -> list[dict]:
    """Analyze and rank multiple combos by discount strength (descending)."""
    results = [analyze(c) for c in combos]
    results.sort(key=lambda r: r["discount_pct"], reverse=True)
    return results


def format_ranking(results: list[dict]) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(
            f"#{i} {r['name']:<22} "
            f"套餐¥{r['combo_price']:.2f}  "
            f"单品¥{r['individual_total']:.2f}  "
            f"省¥{r['savings']:.2f}  "
            f"{r['discount_pct']}%  "
            f"{r['rating']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: combo_analyzer.py <analyze|rank> '<json>' [--json]")
        sys.exit(1)

    cmd = sys.argv[1]
    as_json = "--json" in sys.argv

    if cmd == "analyze":
        data = (
            json.loads(sys.argv[2])
            if len(sys.argv) > 2
            else json.load(sys.stdin)
        )
        result = analyze(data)
        if as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_result(result))

    elif cmd == "rank":
        data = (
            json.loads(sys.argv[2])
            if len(sys.argv) > 2
            else json.load(sys.stdin)
        )
        results = rank(data)
        if as_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(format_ranking(results))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
