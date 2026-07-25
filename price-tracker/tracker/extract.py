"""Extract a product's name/price/currency from its page HTML.

Strategy (generic, no per-site scraper needed for most e-commerce sites):
  1. JSON-LD schema.org Product/Offer blocks (<script type="application/ld+json">).
  2. OpenGraph / product meta tags (og:price:amount, product:price:amount).
  3. Microdata (itemprop="price").

Sites can be added to SITE_OVERRIDES if none of the generic strategies work
for them (e.g. prices only rendered client-side via JavaScript).
"""

import json
import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

REQUEST_TIMEOUT_SECONDS = int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "15"))
USER_AGENT = os.environ.get(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
)

# Per-domain overrides, for sites where the generic strategies fail.
# Each entry is a callable(soup) -> ProductInfo | None. Empty for now.
SITE_OVERRIDES = {}


class ExtractionError(Exception):
    """Raised when no price could be found on the page."""


@dataclass
class ProductInfo:
    name: str | None
    price: float
    currency: str | None


def fetch_html(url: str) -> str:
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    resp.raise_for_status()
    return resp.text


def _parse_price(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    # Strip currency symbols/thousands separators, keep digits, dot, comma
    s = re.sub(r"[^\d.,]", "", s)
    if not s:
        return None
    # Handle "1.234,56" (EU) vs "1,234.56" (US) style thousand/decimal separators
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        # Ambiguous: "120,00" (decimal) vs "1,200" (thousands)
        if re.match(r"^\d{1,3}(,\d{3})+$", s):
            s = s.replace(",", "")
        else:
            s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _from_json_ld(soup: BeautifulSoup) -> ProductInfo | None:
    for tag in soup.find_all("script", type="application/ld+json"):
        raw = tag.string or tag.get_text()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue

        candidates = data if isinstance(data, list) else [data]
        # Some sites nest the real objects under "@graph"
        expanded = []
        for c in candidates:
            if isinstance(c, dict) and "@graph" in c and isinstance(c["@graph"], list):
                expanded.extend(c["@graph"])
            else:
                expanded.append(c)

        for obj in expanded:
            if not isinstance(obj, dict):
                continue
            obj_type = obj.get("@type")
            types = obj_type if isinstance(obj_type, list) else [obj_type]
            if not any(t and "Product" in str(t) for t in types):
                continue

            offers = obj.get("offers")
            if isinstance(offers, list):
                offers = offers[0] if offers else None
            if not isinstance(offers, dict):
                continue

            price = _parse_price(offers.get("price") or offers.get("lowPrice"))
            if price is None:
                continue
            currency = offers.get("priceCurrency")
            name = obj.get("name")
            return ProductInfo(name=name, price=price, currency=currency)
    return None


def _from_meta_tags(soup: BeautifulSoup) -> ProductInfo | None:
    price_meta = (
        soup.find("meta", attrs={"property": "product:price:amount"})
        or soup.find("meta", attrs={"property": "og:price:amount"})
        or soup.find("meta", attrs={"itemprop": "price"})
    )
    if not price_meta or not price_meta.get("content"):
        return None
    price = _parse_price(price_meta["content"])
    if price is None:
        return None

    currency_meta = (
        soup.find("meta", attrs={"property": "product:price:currency"})
        or soup.find("meta", attrs={"property": "og:price:currency"})
        or soup.find("meta", attrs={"itemprop": "priceCurrency"})
    )
    currency = currency_meta["content"] if currency_meta and currency_meta.get("content") else None

    name_meta = soup.find("meta", attrs={"property": "og:title"})
    name = name_meta["content"] if name_meta and name_meta.get("content") else None
    if not name and soup.title:
        name = soup.title.get_text(strip=True)

    return ProductInfo(name=name, price=price, currency=currency)


def _from_microdata(soup: BeautifulSoup) -> ProductInfo | None:
    price_el = soup.find(attrs={"itemprop": "price"})
    if not price_el:
        return None
    price = _parse_price(price_el.get("content") or price_el.get_text())
    if price is None:
        return None
    currency_el = soup.find(attrs={"itemprop": "priceCurrency"})
    currency = currency_el.get("content") if currency_el else None
    name_el = soup.find(attrs={"itemprop": "name"})
    name = name_el.get_text(strip=True) if name_el else (soup.title.get_text(strip=True) if soup.title else None)
    return ProductInfo(name=name, price=price, currency=currency)


def extract_from_html(html: str, url: str) -> ProductInfo:
    domain = urlparse(url).netloc.lower().lstrip("www.")
    if domain in SITE_OVERRIDES:
        soup = BeautifulSoup(html, "html.parser")
        result = SITE_OVERRIDES[domain](soup)
        if result:
            return result

    soup = BeautifulSoup(html, "html.parser")
    for strategy in (_from_json_ld, _from_meta_tags, _from_microdata):
        result = strategy(soup)
        if result:
            return result

    raise ExtractionError(
        f"Could not find a price on {url} using JSON-LD, meta tags, or microdata. "
        "This site may need a custom extractor (see SITE_OVERRIDES in extract.py)."
    )


def extract_from_url(url: str) -> ProductInfo:
    html = fetch_html(url)
    return extract_from_html(html, url)
