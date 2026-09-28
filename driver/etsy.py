"""Etsy Open API v3 の読み取りと、試験用の偽物。

- Etsy のページは取得しない（CLAUDE.md 8、v2 §5.1）。公式 API だけを使う。
- 項目名・エンドポイントは公開の API 仕様からの想定で、Seller App のキーで実際に呼ぶまで [未検証]（v2 §17 #5）。
- 出品・停止の書き込みは、委任（U-002）が出るまで実装しない。
"""
import json
import os
import time
import urllib.request

from . import config as C


class RetryLimitExceeded(Exception):
    pass


def call_with_retry(fn, *, max_attempts=C.MAX_ATTEMPTS, backoff=C.BACKOFF_SECONDS, sleep=time.sleep):
    """回数の上限で止まる（§14 #3）。上限の後は例外を上げ、呼び出し側が例外票を1件作る。"""
    last = None
    for i in range(max_attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001  API の失敗は種類を問わず数える
            last = e
            if i < max_attempts - 1:
                sleep(backoff[min(i, len(backoff) - 1)])
    raise RetryLimitExceeded(f"{max_attempts} 回失敗: {last!r}")


class FakeEtsy:
    """DRY_RUN と §14 の受入テスト用。書き込みは記録するだけ。"""

    def __init__(self, receipts=None, listings=None):
        self.receipts = list(receipts or [])
        self.listings = dict(listings or {})  # listing_id -> {state, views, files:[{sha256}]}
        self.calls: list[tuple] = []
        self.fail_next = 0
        self.crash_after_activate = False

    def _maybe_fail(self):
        if self.fail_next:
            self.fail_next -= 1
            raise ConnectionError("simulated API failure")

    def get_receipts(self, since_ts=0):
        self.calls.append(("get_receipts", since_ts))
        self._maybe_fail()
        return [json.loads(json.dumps(r)) for r in self.receipts]

    def get_listing(self, listing_id):
        self.calls.append(("get_listing", listing_id))
        self._maybe_fail()
        return dict(self.listings[listing_id])

    def get_listing_files(self, listing_id):
        self.calls.append(("get_listing_files", listing_id))
        self._maybe_fail()
        return list(self.listings[listing_id].get("files", []))

    def activate_listing(self, listing_id):
        self.calls.append(("activate_listing", listing_id))
        self.listings.setdefault(listing_id, {})["state"] = "active"
        if self.crash_after_activate:
            self.crash_after_activate = False
            raise SystemExit("simulated crash after activate")

    def deactivate_listing(self, listing_id):
        self.calls.append(("deactivate_listing", listing_id))
        self.listings.setdefault(listing_id, {})["state"] = "inactive"


class HttpEtsy:
    """読み取り専用。キーは環境変数から読み、リポジトリには置かない。"""

    BASE = "https://openapi.etsy.com/v3/application"

    def __init__(self, shop_id=None, api_key=None, token=None):
        self.shop_id = shop_id or os.environ["ETSY_SHOP_ID"]
        self.api_key = api_key or os.environ["ETSY_API_KEY"]
        self.token = token or os.environ["ETSY_READ_TOKEN"]

    def _get(self, path):
        req = urllib.request.Request(
            f"{self.BASE}{path}",
            headers={"x-api-key": self.api_key, "Authorization": f"Bearer {self.token}"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)

    def get_receipts(self, since_ts=0):
        out, offset = [], 0
        while True:
            page = self._get(f"/shops/{self.shop_id}/receipts?min_created={since_ts}&limit=100&offset={offset}")
            out += page.get("results", [])
            offset += 100
            if offset >= page.get("count", 0):
                return out

    def get_listing(self, listing_id):
        return self._get(f"/listings/{listing_id}")

    def get_listing_files(self, listing_id):
        return self._get(f"/shops/{self.shop_id}/listings/{listing_id}/files").get("results", [])

    def activate_listing(self, listing_id):
        raise NotImplementedError("出品の委任（U-002）の前は書き込まない")

    def deactivate_listing(self, listing_id):
        raise NotImplementedError("停止の書き込みは委任の後に実装する。当面は例外票で Shun が止める")
