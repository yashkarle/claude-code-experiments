# Price Tracker

A personal price tracker: add product URLs you're considering buying, and it
periodically checks the price, stores history, and alerts you by email when:

- the price drops to or below a target you set,
- the price drops by more than a threshold percentage since the last check, or
- the price hits its lowest point in the last 90 days (once enough history exists).

## How it works

Most e-commerce product pages (including Ray-Ban's) publish structured price
data for search engines / social previews, via one of:

1. **JSON-LD** (`schema.org` `Product`/`Offer` blocks),
2. **OpenGraph / product meta tags** (`og:price:amount`, `product:price:amount`),
3. **Microdata** (`itemprop="price"`).

`tracker/extract.py` tries these in order, so it works across most retailers
without a site-specific scraper. If a site doesn't publish any of these (or
only renders price via JavaScript), add a custom extractor function to
`SITE_OVERRIDES` in that file.

Prices and history are stored in a local SQLite database at `data/tracker.db`
(not committed to git).

## Setup

```bash
cd price-tracker
python3 -m pip install -r requirements.txt
cp .env.example .env
# edit .env: set SMTP_USERNAME / SMTP_PASSWORD (a Gmail App Password works)
# to your ALERT_TO_EMAIL to receive alerts.
```

## Usage

```bash
# Start tracking a product, optionally with a target price and drop-% threshold
python3 -m tracker.cli add "https://www.ray-ban.com/ireland/sunglasses/RB4427kat%20bio-based-lilac/8056262014486" \
  --target 150 --drop-pct 10

# List everything you're tracking, with latest price and 90-day low
python3 -m tracker.cli list

# See full price history for a product
python3 -m tracker.cli history 1

# Check all tracked products now, evaluate alert rules, send any due alerts
python3 -m tracker.cli check

# Stop tracking a product
python3 -m tracker.cli remove 1
```

Without email configured, `check` still prints any alerts to the console;
configure `.env` to actually receive them.

## Scheduling regular checks

There's no built-in daemon — run `check` on a schedule with cron. Example,
checking twice a day:

```cron
0 9,18 * * * cd /path/to/price-tracker && /usr/bin/python3 -m tracker.cli check >> check.log 2>&1
```

## Alert rules

Configurable per-product (`add --target`, `add --drop-pct`) or via defaults
in `.env` (`DEFAULT_DROP_PCT`, `HISTORICAL_LOW_WINDOW_DAYS`):

| Rule | Fires when | Notes |
|---|---|---|
| `target_price` | price ≤ your target | repeats suppressed while price is unchanged |
| `drop_pct` | price drops ≥ X% vs the previous check | default 10% |
| `historical_low` | price is the lowest seen in the last 90 days | only once ≥30 days of history exist |

## Testing

Because this environment's network policy blocks arbitrary outbound requests
(so the live ray-ban.com page can't be fetched from here), the extractor is
tested against local HTML fixtures in `tests/fixtures/` that mirror the real
JSON-LD/OpenGraph/microdata structures e-commerce sites publish — including a
Ray-Ban-style JSON-LD fixture matching the exact product in this README.

```bash
python3 tests/test_extract.py
python3 tests/test_rules.py
```

Run `add`/`check` against the real URL wherever you actually deploy this (a
machine with normal internet access) to confirm the live page parses too —
the generic strategies should work since Ray-Ban product pages publish
`schema.org` JSON-LD, but this hasn't been verified against the live site.

## Roadmap (v2+)

- **Seasonal / festive price-pattern detection** — once months of history
  accumulate, analyze `price_history` for recurring dips (Black Friday,
  Christmas, summer sales) and predict good times to buy. Deferred because
  it needs real historical depth to be meaningful.
- **Web dashboard** with price-history charts, instead of CLI-only.
- **More alert channels** (Telegram, SMS via Twilio — this repo already has
  Twilio wiring in `gmail_monitor.py` that could be reused).
- **Amazon support** — Amazon actively blocks scraping; would need their
  Product Advertising API (requires an affiliate account) or a paid proxy.
- **JS-rendered sites** with no structured metadata — would need a headless
  browser (Playwright) instead of a plain HTTP fetch.
- Turning this into a shared/multi-user product, if it proves useful
  personally first.
