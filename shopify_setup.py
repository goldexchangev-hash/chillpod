#!/usr/bin/env python3
"""
ChillPod Shopify setup helper.

Creates (or finds) the ChillPod product, optionally attaches product images,
and injects a ChillPod hero section into the live theme's settings_data.json.
Uses only the Python standard library and the Shopify Admin REST API (2024-10).

Authentication uses the OAuth **client credentials grant**: the script trades
your app's Client ID + Client Secret for a short-lived (~24h) Admin API access
token at startup, and transparently refreshes it if Shopify answers 401.
No long-lived token is ever stored, printed, or committed.

DRY-RUN IS THE DEFAULT. Nothing is written to Shopify unless you pass --apply.

--------------------------------------------------------------------------
1. Create the app in the Shopify Dev Dashboard
--------------------------------------------------------------------------
  https://dev.shopify.com/dashboard  -> Apps -> Create app
    -> name it "ChillPod Setup" (any name is fine)
    -> App Settings (or Configuration) -> Admin API access scopes:

         read_products,  write_products     (product + product image steps)
         read_themes,    write_themes       (theme settings_data.json step)
         read_files,     write_files        (optional; only needed if you
                                             later host images via Shopify Files)

    -> Save, then Install the app on your store (Release / Install on store,
       pick your shop, approve the scopes).
    -> App Settings -> Credentials: copy the **Client ID** and **Client Secret**.

  Treat the Client Secret like a password. Never paste it into chat, source
  code, a commit, or a PR. If it leaks, rotate it in Credentials.

  Note: apps created in the Dev Dashboard do NOT expose a copy-paste
  "Admin API access token". This script does not need one - it requests a
  token itself via POST /admin/oauth/access_token (grant_type=client_credentials).

--------------------------------------------------------------------------
2. Set environment variables (never hardcode these)
--------------------------------------------------------------------------
  macOS / Linux (bash, zsh):
    export SHOPIFY_STORE="your-store.myshopify.com"
    export SHOPIFY_CLIENT_ID="<client id from Credentials>"
    export SHOPIFY_CLIENT_SECRET="<client secret from Credentials>"

  Windows PowerShell:
    $env:SHOPIFY_STORE = "your-store.myshopify.com"
    $env:SHOPIFY_CLIENT_ID = "<client id from Credentials>"
    $env:SHOPIFY_CLIENT_SECRET = "<client secret from Credentials>"

--------------------------------------------------------------------------
3. Run
--------------------------------------------------------------------------
  Dry run (default, read-only; shows what WOULD happen):
    python3 shopify_setup.py
    python3 shopify_setup.py --image https://example.com/chillpod.jpg \\
                             --image ./hero-poster.jpg

  Apply (actually creates the product, uploads images, updates the theme):
    python3 shopify_setup.py --apply --image ./hero-poster.jpg

  Skip individual steps:
    python3 shopify_setup.py --apply --skip-theme
    python3 shopify_setup.py --apply --skip-product --skip-images

Requires Python 3.8+. No third-party packages.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

API_VERSION = "2024-10"

PRODUCT_TITLE = "ChillPod - No-Power Phone Cooler for Saunas"
PRODUCT_HANDLE = "chillpod"
PRODUCT_BODY_HTML = (
    "<p><strong>ChillPod</strong> is a no-power phone cooler built for saunas. "
    "Slip your phone in before you step into the heat and it stays cool enough "
    "to keep working while you sweat.</p>"
    "<ul>"
    "<li>No fans. No batteries. No power - nothing to charge, nothing to break.</li>"
    "<li>Protects your phone from overheating and heat shutdown in sauna temperatures.</li>"
    "<li>Simple, passive cooling that works every session.</li>"
    "</ul>"
    "<p><em>Patent Pending.</em></p>"
)
PRODUCT_VENDOR = "ChillPod"
PRODUCT_TYPE = "Phone Accessory"
PRODUCT_TAGS = "sauna, phone cooler, no power, patent pending"
VARIANT_PRICE = "49.99"
VARIANT_SKU = "CHILLPOD-001"

THEME_SECTION_KEY = "chillpod_hero"
IMAGE_UPLOAD_PAUSE_SECONDS = 0.5


# --------------------------------------------------------------------------
# Output helpers
# --------------------------------------------------------------------------

def log(msg: str = "") -> None:
    print(redact(msg), flush=True)


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {redact(msg)}", file=sys.stderr, flush=True)
    sys.exit(code)


# --------------------------------------------------------------------------
# Shopify Admin REST client (stdlib only)
# --------------------------------------------------------------------------

_SECRETS: List[str] = []


def register_secret(value: str) -> None:
    """Remember a sensitive string so redact() can scrub it from any output."""
    if value and value not in _SECRETS:
        _SECRETS.append(value)


def redact(text: str) -> str:
    """Replace every registered secret (and anything token-shaped) with [REDACTED]."""
    for s in _SECRETS:
        if s:
            text = text.replace(s, "[REDACTED]")
    # Belt-and-braces: mask any token-like values Shopify might echo back.
    text = re.sub(r"shp(at|ca|ss|ua)_[A-Za-z0-9]+", "[REDACTED]", text)
    text = re.sub(r'("(?:access_token|client_secret|client_id)"\s*:\s*")[^"]*(")',
                  r"\1[REDACTED]\2", text)
    return text


class ShopifyError(Exception):
    def __init__(self, status: int, method: str, url: str, body: str):
        self.status = status
        self.method = method
        self.url = url
        self.body = redact(body)
        snippet = self.body.strip().replace("\n", " ")
        if len(snippet) > 400:
            snippet = snippet[:400] + "..."
        super().__init__(f"HTTP {status} from {method} {redact(url)}: {snippet or '<empty body>'}")


def _http_json(
    method: str,
    url: str,
    headers: Dict[str, str],
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Perform one HTTPS request and return the parsed JSON body.

    Request bodies are never included in errors: they may contain secrets.
    """
    data = None
    hdrs = dict(headers)
    hdrs.setdefault("Accept", "application/json")
    hdrs.setdefault("User-Agent", "chillpod-shopify-setup/1.0 (python-stdlib)")
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise ShopifyError(e.code, method, url, raw) from None
    except urllib.error.URLError as e:
        raise ShopifyError(0, method, url, f"network error: {e.reason}") from None

    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ShopifyError(status, method, url, f"non-JSON response: {raw}") from None


class ShopifyClient:
    """Admin REST client that authenticates via the client credentials grant."""

    def __init__(self, store: str, client_id: str, client_secret: str):
        store = store.strip().lower()
        store = re.sub(r"^https?://", "", store).rstrip("/")
        self.store = store
        self._client_id = client_id
        self._client_secret = client_secret
        register_secret(client_id)
        register_secret(client_secret)
        self.base = f"https://{self.store}/admin/api/{API_VERSION}"
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0

    # -- auth ---------------------------------------------------------------

    def fetch_access_token(self) -> None:
        """POST /admin/oauth/access_token (grant_type=client_credentials)."""
        url = f"https://{self.store}/admin/oauth/access_token"
        body = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        resp = _http_json("POST", url, headers={}, payload=body)
        token = resp.get("access_token")
        if not token or not isinstance(token, str):
            raise ShopifyError(200, "POST", url,
                               "token response did not include access_token")
        self._token = token
        register_secret(token)
        try:
            ttl = float(resp.get("expires_in", 86400))
        except (TypeError, ValueError):
            ttl = 86400.0
        self._token_expires_at = time.time() + ttl
        scope = resp.get("scope", "")
        log(f"Authenticated with {self.store} via client credentials "
            f"(token valid ~{int(ttl // 3600)}h; scopes: {scope or 'n/a'})")

    def _auth_headers(self) -> Dict[str, str]:
        # Refresh a minute early so a long-running image batch doesn't hit 401.
        if self._token is None or time.time() > self._token_expires_at - 60:
            self.fetch_access_token()
        assert self._token is not None
        return {"X-Shopify-Access-Token": self._token}

    # -- requests -----------------------------------------------------------

    def request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base}/{path.lstrip('/')}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        try:
            return _http_json(method, url, self._auth_headers(), payload)
        except ShopifyError as e:
            if e.status != 401:
                raise
            log("Got 401 from Admin API; refreshing access token and retrying once...")
            self.fetch_access_token()
            return _http_json(method, url, self._auth_headers(), payload)

    def get(self, path: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        return self.request("GET", path, params=params)

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.request("POST", path, payload=payload)

    def put(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.request("PUT", path, payload=payload)


# --------------------------------------------------------------------------
# Step 1: product
# --------------------------------------------------------------------------

def find_product(client: ShopifyClient) -> Optional[Dict[str, Any]]:
    """Return the product whose title matches PRODUCT_TITLE exactly, or None."""
    # `title` is a substring filter server-side; enforce exact match here.
    resp = client.get("products.json", params={"title": PRODUCT_TITLE, "limit": "250"})
    for product in resp.get("products", []):
        if product.get("title") == PRODUCT_TITLE:
            return product
    # Fallback: handle lookup, in case the title was edited in admin.
    resp = client.get("products.json", params={"handle": PRODUCT_HANDLE, "limit": "1"})
    for product in resp.get("products", []):
        if product.get("title") == PRODUCT_TITLE:
            return product
    return None


def build_product_payload() -> Dict[str, Any]:
    return {
        "product": {
            "title": PRODUCT_TITLE,
            "handle": PRODUCT_HANDLE,
            "body_html": PRODUCT_BODY_HTML,
            "vendor": PRODUCT_VENDOR,
            "product_type": PRODUCT_TYPE,
            "tags": PRODUCT_TAGS,
            "status": "active",
            "variants": [
                {
                    "price": VARIANT_PRICE,
                    "sku": VARIANT_SKU,
                    "inventory_management": "shopify",
                    "inventory_policy": "deny",
                    "requires_shipping": True,
                    "taxable": True,
                }
            ],
        }
    }


def step_product(client: ShopifyClient, apply: bool, summary: List[str]) -> Optional[int]:
    log("== Product ==")
    existing = find_product(client)
    if existing:
        pid, handle = existing["id"], existing.get("handle")
        log(f"Found existing product: id={pid} handle={handle}")
        summary.append(f"Product: found existing (id={pid}, handle={handle})")
        return pid

    payload = build_product_payload()
    if not apply:
        log(f"Not found. Would POST /products.json to create:")
        log(json.dumps(payload, indent=2))
        summary.append("Product: NOT found; would be created (dry-run)")
        return None

    log("Not found. Creating product...")
    resp = client.post("products.json", payload)
    product = resp.get("product", {})
    pid, handle = product.get("id"), product.get("handle")
    variants = product.get("variants", [])
    vsku = variants[0].get("sku") if variants else None
    log(f"Created product: id={pid} handle={handle} variant_sku={vsku}")
    summary.append(f"Product: CREATED (id={pid}, handle={handle})")
    return pid


# --------------------------------------------------------------------------
# Step 2: images
# --------------------------------------------------------------------------

def is_url(value: str) -> bool:
    return value.lower().startswith(("http://", "https://"))


def build_image_payload(source: str, position: int) -> Tuple[Dict[str, Any], str]:
    """Return (payload, description). Local files are base64-encoded as `attachment`."""
    image: Dict[str, Any] = {"position": position, "alt": PRODUCT_TITLE}
    if is_url(source):
        image["src"] = source
        return {"image": image}, f"URL {source}"

    path = Path(source).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"image file not found: {source}")
    mime, _ = mimetypes.guess_type(path.name)
    if not mime or not mime.startswith("image/"):
        raise ValueError(f"{source} does not look like an image (guessed type: {mime})")
    data = path.read_bytes()
    image["attachment"] = base64.b64encode(data).decode("ascii")
    image["filename"] = path.name
    return {"image": image}, f"local file {path} ({len(data):,} bytes, {mime})"


def step_images(
    client: ShopifyClient,
    product_id: Optional[int],
    images: List[str],
    apply: bool,
    summary: List[str],
) -> None:
    log("\n== Images ==")
    if not images:
        log("No --image arguments provided; skipping image upload.")
        summary.append("Images: none provided (skipped)")
        return

    # Validate every source up front so a typo in the 3rd path doesn't leave
    # a half-uploaded gallery behind.
    prepared: List[Tuple[Dict[str, Any], str]] = []
    for i, src in enumerate(images, start=1):
        try:
            prepared.append(build_image_payload(src, i))
        except (FileNotFoundError, ValueError, OSError) as e:
            fail(f"Image #{i}: {e}")

    if not apply:
        for _, desc in prepared:
            log(f"Would upload {desc}")
        target = f"product {product_id}" if product_id else "the newly created product"
        log(f"({len(prepared)} image(s) would be POSTed to /products/{{id}}/images.json for {target})")
        summary.append(f"Images: {len(prepared)} would be uploaded (dry-run)")
        return

    if product_id is None:
        fail("Cannot upload images: no product id available.")

    uploaded = 0
    for idx, (payload, desc) in enumerate(prepared):
        if idx > 0:
            time.sleep(IMAGE_UPLOAD_PAUSE_SECONDS)
        log(f"Uploading {desc} ...")
        resp = client.post(f"products/{product_id}/images.json", payload)
        img = resp.get("image", {})
        log(f"  -> image id={img.get('id')} src={img.get('src')}")
        uploaded += 1
    summary.append(f"Images: uploaded {uploaded} to product {product_id}")


# --------------------------------------------------------------------------
# Step 3: theme settings_data.json
# --------------------------------------------------------------------------

def parse_settings_data(raw: str) -> Dict[str, Any]:
    """
    Shopify's settings_data.json usually starts with a /* ... */ comment block
    before the JSON object. Strip anything before the first '{' and after the
    last '}' and also drop any stray line comments, then parse.
    """
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("settings_data.json does not contain a JSON object")
    body = raw[start : end + 1]
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        # Remove // line comments and /* */ block comments outside of strings.
        body = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
        body = re.sub(r"^\s*//.*$", "", body, flags=re.MULTILINE)
        return json.loads(body)


def build_chillpod_section() -> Dict[str, Any]:
    """
    Online Store 2.0 section data as stored in settings_data.json:
      {"type": <section file name>, "settings": {...},
       "blocks": {<block_id>: {"type": ..., "settings": {...}}}, "block_order": [...]}

    Assumption: we don't know which theme is live, so the section is written
    as a theme-agnostic payload using generic block types (hero / features /
    text) and common setting names (heading, subheading, text, button_label,
    button_link). Shopify accepts arbitrary keys in settings_data.json; a theme
    only renders sections/blocks whose `type` matches a schema it ships. If
    the live theme has no `sections/chillpod-hero.liquid`, add one whose
    schema declares these block types and settings, or rename `type` values
    below to match the theme's own hero/rich-text sections.
    """
    return {
        "type": "chillpod-hero",
        "settings": {
            "color_scheme": "background-1",
            "padding_top": 36,
            "padding_bottom": 36,
        },
        "blocks": {
            "chillpod_hero_main": {
                "type": "hero",
                "settings": {
                    "heading": "ChillPod",
                    "subheading": "No-power phone cooler for saunas",
                    "button_label": "Shop Now",
                    "button_link": f"/products/{PRODUCT_HANDLE}",
                },
            },
            "chillpod_features": {
                "type": "features",
                "settings": {
                    "heading": "Why ChillPod",
                    "text": "No fans. No batteries. No power. Just cool.",
                },
            },
            "chillpod_patent": {
                "type": "text",
                "settings": {
                    "text": "<strong>Patent Pending</strong>",
                },
            },
        },
        "block_order": ["chillpod_hero_main", "chillpod_features", "chillpod_patent"],
    }


def step_theme(client: ShopifyClient, apply: bool, summary: List[str]) -> None:
    log("\n== Theme ==")
    themes = client.get("themes.json").get("themes", [])
    main_theme = next((t for t in themes if t.get("role") == "main"), None)
    if not main_theme:
        fail("No theme with role 'main' found in /themes.json")
    theme_id, theme_name = main_theme["id"], main_theme.get("name")
    log(f"Main theme: id={theme_id} name={theme_name!r}")

    asset_key = "config/settings_data.json"
    asset_resp = client.get(
        f"themes/{theme_id}/assets.json", params={"asset[key]": asset_key}
    )
    asset = asset_resp.get("asset", {})
    raw = asset.get("value")
    if raw is None and asset.get("attachment"):
        raw = base64.b64decode(asset["attachment"]).decode("utf-8", errors="replace")
    if raw is None:
        fail(f"Could not read {asset_key} from theme {theme_id}")

    try:
        settings = parse_settings_data(raw)
    except (ValueError, json.JSONDecodeError) as e:
        fail(f"Could not parse {asset_key}: {e}")

    current = settings.get("current")
    if not isinstance(current, dict):
        # "current" may be a preset name string on some themes; fall back to
        # the named preset so we edit a real dict.
        presets = settings.get("presets", {})
        if isinstance(current, str) and isinstance(presets.get(current), dict):
            log(f"'current' points at preset {current!r}; editing that preset.")
            settings["current"] = dict(presets[current])
            current = settings["current"]
        else:
            fail(f"{asset_key} has no editable 'current' object")

    sections = current.setdefault("sections", {})
    order = current.setdefault("content_for_index", [])
    if not isinstance(sections, dict) or not isinstance(order, list):
        fail("Unexpected structure for current.sections / current.content_for_index")

    already_section = THEME_SECTION_KEY in sections
    already_ordered = THEME_SECTION_KEY in order
    log(f"Section '{THEME_SECTION_KEY}' present: {already_section}; "
        f"in content_for_index: {already_ordered}")
    log(f"Existing content_for_index: {order}")

    new_section = build_chillpod_section()
    if already_section and already_ordered and sections[THEME_SECTION_KEY] == new_section:
        log("Theme already up to date; nothing to do.")
        summary.append(f"Theme: '{THEME_SECTION_KEY}' already present in {theme_name!r} (no change)")
        return

    if not apply:
        verb = "update" if already_section else "add"
        log(f"Would {verb} section '{THEME_SECTION_KEY}' in {asset_key}:")
        log(json.dumps({THEME_SECTION_KEY: new_section}, indent=2))
        if not already_ordered:
            log(f"Would prepend '{THEME_SECTION_KEY}' to content_for_index -> "
                f"{[THEME_SECTION_KEY] + order}")
        log(f"Would PUT /themes/{theme_id}/assets.json (key={asset_key})")
        summary.append(f"Theme: would {verb} '{THEME_SECTION_KEY}' in {theme_name!r} (dry-run)")
        return

    sections[THEME_SECTION_KEY] = new_section
    if not already_ordered:
        order.insert(0, THEME_SECTION_KEY)

    log(f"Writing {asset_key} to theme {theme_id} ...")
    client.put(
        f"themes/{theme_id}/assets.json",
        {"asset": {"key": asset_key, "value": json.dumps(settings, indent=2)}},
    )
    log("Theme updated.")
    summary.append(f"Theme: '{THEME_SECTION_KEY}' written to {theme_name!r} (id={theme_id})")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Set up the ChillPod product, images and theme hero in Shopify. "
                    "Dry-run by default; pass --apply to write.",
    )
    p.add_argument("--apply", action="store_true",
                   help="Actually write to Shopify (default is a read-only dry run).")
    p.add_argument("--image", action="append", default=[], metavar="URL_OR_PATH",
                   help="Product image to upload; repeatable. URL -> src, local file -> base64 attachment.")
    p.add_argument("--skip-product", action="store_true", help="Skip the product step.")
    p.add_argument("--skip-images", action="store_true", help="Skip the image step.")
    p.add_argument("--skip-theme", action="store_true", help="Skip the theme step.")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    store = os.environ.get("SHOPIFY_STORE", "").strip()
    client_id = os.environ.get("SHOPIFY_CLIENT_ID", "").strip()
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET", "").strip()
    missing = [
        name for name, val in (
            ("SHOPIFY_STORE", store),
            ("SHOPIFY_CLIENT_ID", client_id),
            ("SHOPIFY_CLIENT_SECRET", client_secret),
        ) if not val
    ]
    if missing:
        fail(
            f"missing environment variable(s): {', '.join(missing)}.\n"
            "  export SHOPIFY_STORE=\"your-store.myshopify.com\"\n"
            "  export SHOPIFY_CLIENT_ID=\"...\"       (Dev Dashboard -> App Settings -> Credentials)\n"
            "  export SHOPIFY_CLIENT_SECRET=\"...\"   (same page; keep it secret)\n"
            "See the docstring at the top of this file for setup steps."
        )

    client = ShopifyClient(store, client_id, client_secret)
    mode = "APPLY (writes enabled)" if args.apply else "DRY RUN (no writes; pass --apply to write)"
    log(f"Store: {client.store}   API: {API_VERSION}   Mode: {mode}")

    summary: List[str] = []
    product_id: Optional[int] = None
    try:
        client.fetch_access_token()
        log()
        if args.skip_product:
            log("== Product ==\nSkipped (--skip-product).")
            summary.append("Product: skipped")
            if not args.skip_images and args.image:
                existing = find_product(client)
                product_id = existing["id"] if existing else None
        else:
            product_id = step_product(client, args.apply, summary)

        if args.skip_images:
            log("\n== Images ==\nSkipped (--skip-images).")
            summary.append("Images: skipped")
        else:
            step_images(client, product_id, args.image, args.apply, summary)

        if args.skip_theme:
            log("\n== Theme ==\nSkipped (--skip-theme).")
            summary.append("Theme: skipped")
        else:
            step_theme(client, args.apply, summary)
    except ShopifyError as e:
        if "/admin/oauth/access_token" in e.url:
            hint = (" (token exchange failed: check SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET "
                    "and that the app is installed on this store)")
        elif e.status in (401, 403):
            hint = " (check that the app is installed on the store and has the required scopes)"
        elif e.status == 404:
            hint = " (check SHOPIFY_STORE, e.g. your-store.myshopify.com)"
        elif e.status == 429:
            hint = " (rate limited; wait a moment and re-run)"
        else:
            hint = ""
        fail(redact(f"{e}{hint}"))

    log("\n== Summary ==")
    for line in summary:
        log(f"- {line}")
    if not args.apply:
        log("\nDry run complete. Re-run with --apply to make these changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
