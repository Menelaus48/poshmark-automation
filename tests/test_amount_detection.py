#!/usr/bin/env python3
"""Unit tests for balance and transfer amount detection helpers."""

import unittest

from posh_autoredeem import parse_money, extract_transfer_amount


class FakeLocator:
    """Minimal stand-in for Playwright's Locator used in tests."""

    def __init__(self, texts):
        if isinstance(texts, (list, tuple)):
            self._texts = list(texts)
        else:
            self._texts = [texts]

    def count(self):
        return len(self._texts)

    @property
    def first(self):
        return FakeLocator(self._texts[0])

    def inner_text(self):
        return str(self._texts[0])

    def locator(self, *_args, **_kwargs):
        return self


class FakePage:
    """Simple fake Page that supports the subset extract_transfer_amount needs."""

    def __init__(self, amount_text=None, body_text=""):
        self._amount_text = amount_text
        self._body_text = body_text

    def locator(self, selector):  # pylint: disable=unused-argument
        # Basic heuristic: if the selector is looking for AMOUNT text, return the stub.
        if "AMOUNT" in selector and self._amount_text is not None:
            return FakeLocator(self._amount_text)
        raise RuntimeError("Locator not found")

    def inner_text(self, target):
        if target == "body":
            return self._body_text
        raise RuntimeError("Unsupported inner_text target")

    def content(self):
        return self._body_text


class ParseMoneyTests(unittest.TestCase):
    def test_parses_amount_with_split_spans(self):
        html = "<div class='amount'><span>$</span><span>94.50</span></div>"
        self.assertEqual(parse_money(html), 94.50)

    def test_prefers_balance_keyword_over_fee(self):
        html = (
            "<div>Instant Transfer - $2 fee</div>"
            "<div>Available Balance</div>"
            "<div>$275.70</div>"
        )
        self.assertEqual(parse_money(html), 275.70)

    def test_returns_largest_amount_when_no_keywords(self):
        html = "<p>$0.35 fee</p><p>$0.75 tip</p><p>$35.10 payout</p>"
        self.assertEqual(parse_money(html), 35.10)

    def test_ignores_instant_transfer_fee(self):
        html = (
            "<div>Instant Transfer</div>"
            "<div>$2 fee</div>"
            "<div>Available Balance</div>"
            "<div>$94.50</div>"
        )
        self.assertEqual(parse_money(html), 94.50)

    def test_returns_none_if_only_instant_transfer_fee_present(self):
        html = "<div>Instant Transfer - $2 fee</div>"
        self.assertIsNone(parse_money(html))

    def test_returns_none_when_no_amount_present(self):
        html = "<div>No dollars here</div>"
        self.assertIsNone(parse_money(html))


class ExtractTransferAmountTests(unittest.TestCase):
    def test_extracts_from_labelled_amount(self):
        page = FakePage(amount_text="Amount $94.50")
        self.assertEqual(extract_transfer_amount(page), 94.50)

    def test_falls_back_to_body_text(self):
        page = FakePage(amount_text=None, body_text="Your total is $120.25")
        self.assertEqual(extract_transfer_amount(page), 120.25)


if __name__ == "__main__":
    unittest.main()
