"""Command-line interface: add / list / history / check / remove."""

import argparse
import sys
import time
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from . import db
from .extract import ExtractionError, extract_from_url
from .notify import EmailNotifier, send_alert
from .rules import evaluate, should_send


def cmd_add(args):
    existing = db.get_product_by_url(args.url)
    if existing:
        print(f"Product already tracked (id={existing['id']}): {existing['url']}")
        return

    try:
        info = extract_from_url(args.url)
    except ExtractionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching {args.url}: {e}", file=sys.stderr)
        sys.exit(1)

    name = args.name or info.name or args.url
    product_id = db.add_product(args.url, name, info.currency, args.target, args.drop_pct)
    db.record_price(product_id, info.price)
    print(f"Added product id={product_id}: {name}")
    price_label = f"{info.currency} {info.price:.2f}" if info.currency else f"{info.price:.2f}"
    print(f"  Current price: {price_label}")
    if args.target:
        print(f"  Target price: {args.target:.2f}")
    if args.drop_pct:
        print(f"  Drop alert threshold: {args.drop_pct:.0f}%")


def cmd_list(args):
    products = db.list_products(active_only=not args.all)
    if not products:
        print("No products tracked yet. Use `add <url>` to start tracking one.")
        return

    for p in products:
        latest = db.get_latest_price(p["id"])
        since = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        history_90d = db.get_price_history(p["id"], since=since)
        low_90d = min((h["price"] for h in history_90d), default=None)

        status = "" if p["active"] else " [inactive]"
        print(f"[{p['id']}] {p['name']}{status}")
        print(f"    {p['url']}")
        if latest:
            price_label = f"{p['currency']} {latest['price']:.2f}" if p["currency"] else f"{latest['price']:.2f}"
            line = f"    Latest: {price_label} (checked {latest['checked_at']})"
            if low_90d is not None:
                line += f"  |  90d low: {low_90d:.2f}"
            print(line)
        else:
            print("    No price recorded yet.")
        if p["target_price"]:
            print(f"    Target: {p['target_price']:.2f}  |  Drop alert: {p['drop_pct'] or '-'}%")


def cmd_history(args):
    product = db.get_product(args.id)
    if not product:
        print(f"No product with id={args.id}", file=sys.stderr)
        sys.exit(1)
    history = db.get_price_history(args.id)
    print(f"Price history for [{product['id']}] {product['name']}:")
    if not history:
        print("  (no history yet)")
        return
    for h in history:
        print(f"  {h['checked_at']}  {product['currency'] or ''} {h['price']:.2f}")


def cmd_check(args):
    products = [db.get_product(args.id)] if args.id else db.list_products(active_only=True)
    products = [p for p in products if p]
    if not products:
        print("No products to check.")
        return

    notifier = EmailNotifier()
    any_alerts = False

    for i, product in enumerate(products):
        if i > 0:
            time.sleep(args.delay)
        print(f"Checking [{product['id']}] {product['name']}...")
        try:
            info = extract_from_url(product["url"])
        except Exception as e:
            print(f"  Failed to fetch price: {e}", file=sys.stderr)
            continue

        row_id = db.record_price(product["id"], info.price)
        print(f"  Price: {product['currency'] or ''} {info.price:.2f}")

        fired = evaluate(product, row_id, info.price)
        for rule in fired:
            if not should_send(product["id"], rule):
                continue
            print(f"  ALERT ({rule.rule}): {rule.message}")
            any_alerts = True
            db.record_alert(product["id"], rule.rule, info.price)
            if notifier.is_configured():
                try:
                    send_alert(notifier, product["name"], product["url"], [rule])
                except Exception as e:
                    print(f"  Failed to send email alert: {e}", file=sys.stderr)
            else:
                print("  (email not configured - set SMTP_* vars in .env to receive alerts)")

    if not any_alerts:
        print("No alerts triggered.")


def cmd_remove(args):
    product = db.get_product(args.id)
    if not product:
        print(f"No product with id={args.id}", file=sys.stderr)
        sys.exit(1)
    db.remove_product(args.id)
    print(f"Removed [{args.id}] {product['name']} from tracking.")


def build_parser():
    parser = argparse.ArgumentParser(prog="tracker", description="Personal price tracker")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Start tracking a product URL")
    p_add.add_argument("url")
    p_add.add_argument("--name", help="Friendly name (defaults to page title)")
    p_add.add_argument("--target", type=float, help="Alert when price drops to/below this value")
    p_add.add_argument("--drop-pct", type=float, help="Alert when price drops this %% vs previous check")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List tracked products")
    p_list.add_argument("--all", action="store_true", help="Include removed/inactive products")
    p_list.set_defaults(func=cmd_list)

    p_hist = sub.add_parser("history", help="Show price history for a product")
    p_hist.add_argument("id", type=int)
    p_hist.set_defaults(func=cmd_history)

    p_check = sub.add_parser("check", help="Check prices now and send alerts")
    p_check.add_argument("--id", type=int, help="Check only this product id")
    p_check.add_argument("--delay", type=float, default=2.0, help="Seconds to wait between requests")
    p_check.set_defaults(func=cmd_check)

    p_remove = sub.add_parser("remove", help="Stop tracking a product")
    p_remove.add_argument("id", type=int)
    p_remove.set_defaults(func=cmd_remove)

    return parser


def main():
    load_dotenv()
    db.init_db()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
