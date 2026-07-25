"""Tests for tracker.extract using local HTML fixtures.

Note: this environment's network policy blocks outbound requests to
arbitrary sites (including ray-ban.com), so these tests exercise the
extraction logic against realistic *local* fixtures that mirror the
schema.org JSON-LD / OpenGraph / microdata patterns real e-commerce sites
(Ray-Ban among them) publish, rather than hitting the live URL. Re-run
`tracker check`/`tracker add` against the real URL wherever you deploy this
(a machine with normal internet access) to confirm the live page parses too.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tracker.extract import extract_from_html, ExtractionError, _parse_price

FIXTURES = Path(__file__).parent / "fixtures"


def test_json_ld_product_offer_rayban_style():
    html = (FIXTURES / "jsonld_product.html").read_text()
    info = extract_from_html(html, "https://www.ray-ban.com/ireland/sunglasses/RB4427/8056262014486")
    assert info.name == "RB4427 Kat Bio-Based Lilac"
    assert info.price == 173.0
    assert info.currency == "EUR"


def test_json_ld_graph_wrapped():
    html = (FIXTURES / "jsonld_graph.html").read_text()
    info = extract_from_html(html, "https://example.com/product/1")
    assert info.price == 49.99
    assert info.currency == "USD"


def test_meta_tag_fallback():
    html = (FIXTURES / "meta_tags_only.html").read_text()
    info = extract_from_html(html, "https://example.com/product/2")
    assert info.price == 89.5
    assert info.currency == "EUR"
    assert info.name == "Generic Product Title"


def test_microdata_fallback():
    html = (FIXTURES / "microdata_only.html").read_text()
    info = extract_from_html(html, "https://example.com/product/3")
    assert info.price == 25.0
    assert info.currency == "GBP"


def test_no_price_raises():
    html = "<html><head><title>No price here</title></head><body>Nothing</body></html>"
    try:
        extract_from_html(html, "https://example.com/nope")
        assert False, "expected ExtractionError"
    except ExtractionError:
        pass


def test_parse_price_eu_format():
    assert _parse_price("1.234,56") == 1234.56


def test_parse_price_us_format():
    assert _parse_price("1,234.56") == 1234.56


def test_parse_price_simple_decimal():
    assert _parse_price("173,00") == 173.00
    assert _parse_price("€173.00") == 173.00


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"PASS {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
