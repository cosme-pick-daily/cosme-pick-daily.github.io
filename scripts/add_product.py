"""data/products.json に商品を1件追記し、必要なら git commit & push する。

使い方:
  python scripts/add_product.py --name "商品名" --price 1980 \
      --image "https://..." --url "https://hb.afl.rakuten.co.jp/..." [--date 2026-10-28] [--push]

他のスクリプトからは add_product(...) と publish(...) を import して使える。
commit するのは data/products.json だけなので、.env などが誤って入ることはない。
"""

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_PATH = REPO_ROOT / "data" / "products.json"


def _require_https(value, field):
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{field} は https:// で始まるURLにしてください: {value}")


def load_products():
    if not PRODUCTS_PATH.exists():
        return []
    with PRODUCTS_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{PRODUCTS_PATH} の中身が配列ではありません")
    return data


def save_products(products):
    PRODUCTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PRODUCTS_PATH.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
        f.write("\n")


def add_product(name, price, image, url, added=None):
    """商品を追記する。同じURLの商品が既にあれば追加せず False を返す。"""
    name = name.strip()
    if not name:
        raise ValueError("name が空です")
    price = int(price)
    if price < 0:
        raise ValueError("price が負の値です")
    _require_https(url, "url")
    if image:
        _require_https(image, "image")
    added = added or datetime.date.today().isoformat()
    try:
        datetime.date.fromisoformat(added)
    except ValueError:
        raise ValueError(f"日付は YYYY-MM-DD 形式にしてください: {added}") from None

    products = load_products()
    if any(p.get("url") == url for p in products):
        return False
    products.append({
        "name": name,
        "price": price,
        "image": image or "",
        "url": url,
        "added": added,
    })
    save_products(products)
    return True


def _git(*args):
    subprocess.run(["git", *args], cwd=REPO_ROOT, check=True)


def publish(message):
    """data/products.json だけを commit して push する。"""
    _git("add", "--", "data/products.json")
    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--", "data/products.json"],
        cwd=REPO_ROOT,
    )
    if staged.returncode == 0:
        print("変更がないので commit しません")
        return
    _git("commit", "-m", message, "--", "data/products.json")
    _git("push")


def main():
    parser = argparse.ArgumentParser(description="products.json に商品を追加する")
    parser.add_argument("--name", required=True, help="商品名")
    parser.add_argument("--price", required=True, type=int, help="価格（円）")
    parser.add_argument("--image", default="", help="商品画像のURL (https)")
    parser.add_argument("--url", required=True, help="楽天アフィリエイトリンク (https)")
    parser.add_argument("--date", help="追加日 YYYY-MM-DD（省略時は今日）")
    parser.add_argument("--push", action="store_true", help="追加後に commit & push する")
    args = parser.parse_args()

    try:
        added = add_product(args.name, args.price, args.image, args.url, args.date)
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1

    if not added:
        print("同じURLの商品が既にあるので追加しませんでした")
        return 0
    print(f"追加しました: {args.name}")

    if args.push:
        publish(f"Add product: {args.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
