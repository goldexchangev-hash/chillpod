# Temporarily disable ordering on ichillpod.com — inventory hard stop, storefront unchanged

**Revised plan (merchant decision, 2026-09-27):** the Dawn storefront keeps its exact current
appearance — Buy Now buttons, homepage CTAs, header links, Shop Pay / accelerated checkout,
all purchase UI stay as they are. Orders are stopped by **Shopify inventory only**. The
"Coming soon" message is shown **only where a customer actually attempts to check out**
(cart / checkout), never on the product page, homepage or header.

**Nothing in this repo changes the live store.** This PR is documentation plus one optional
copy-paste cart-only snippet. Orders on ichillpod.com are blocked only after a human performs
§1 in Shopify Admin. Merging this PR by itself does nothing to live checkout.

| | |
| --- | --- |
| Live storefront | https://ichillpod.com (Shopify Online Store) |
| Shop | `yz0m1m-ru.myshopify.com` (admin handle `ichillpod`; `ichillpod.myshopify.com` 301s to `ichillpod.com`) |
| Live theme | **Dawn — payment icons preview**, Dawn schema **16.0.0**, theme id `188025995375`, role `main`. Cart type: *notification* (no cart drawer) |
| Product | `iChillPod - No-Power Phone Cooler for Saunas`, handle `chillpod`, product id `15554226356335`, status Active |
| Variant | `Default Title`, variant id **`67578266419311`**, **$29.95**, single variant |
| Inventory today | **Not tracked** (`inventory_management: null`) → unlimited; `available: true` |
| Cart permalink to neutralise | `https://ichillpod.com/cart/67578266419311:1` (also via `ichillpod.myshopify.com/cart/67578266419311:1`; used by this repo's landing page) — today it **302s straight into Shop Pay checkout** |
| This repo | `goldexchangev-hash/chillpod` — static Render landing page. **Not** the Dawn theme. |

Facts read from the public storefront (`/products/chillpod.js`, page HTML, `Shopify.theme`) on
2026-09-27. Re-check before applying.

Message to use where a message is shown: **"Coming soon — should be available within the next 30 days."**

---

## 0. Capture the current state before changing anything

Fill the last column when applying; keep it with the PR / ticket. Revert depends on it.

| Item | Where | Observed 2026-09-27 | At apply time |
| --- | --- | --- | --- |
| *Track quantity* on the variant | Admin → Products → iChillPod → **Inventory** card | **Off** (not tracked = unlimited) | |
| Available quantity per location | same card (after tracking is on, one row per location) | n/a | |
| *Continue selling when out of stock* | same card (visible only when tracking is on) | n/a | |
| Product status / channels | Products → iChillPod → Status, Publishing | Active; Online Store (+ any others — leave) | |
| Price / compare-at | variant | $29.95 / — | |
| Cart template sections | Theme editor → Cart | `main-cart-items`, `main-cart-footer` (stock Dawn) | |
| Permalink behaviour | `curl -sI https://ichillpod.com/cart/67578266419311:1` | 302 → `shop.app/checkout/…/shoppay` | |

Optional safety net: Themes → live theme → **⋯ → Duplicate** before touching the Cart template
in §3-B. Not needed for §1 (Admin only).

---

## 1. Hard stop — inventory 0 in Shopify Admin (REQUIRED; the only step that blocks orders)

1. Shopify Admin → **Products** → *iChillPod - No-Power Phone Cooler for Saunas*.
2. **Inventory** card → tick **Track quantity**. *(Store-specific gotcha: the variant is
   currently untracked. Until tracking is on, a quantity of 0 has no effect and the item stays
   purchasable.)*
3. Make sure **Continue selling when out of stock** is **unticked**.
4. Set **Available** to **0** for **every** location row shown (Shop location, any warehouse,
   Shopify Fulfillment Network, etc.).
5. **Save.**
6. Do **not**: set to Draft, unpublish from Online Store or any channel, delete the variant or
   media, change price / compare-at, archive, add URL redirects, password-protect the store,
   disable Shop Pay or payment providers. None of those are needed and some are irreversible.

Within ~1 minute (CDN) Shopify enforces sold-out server-side: `product.available == false`,
`POST /cart/add` → 422 "sold out", checkout refuses the line item. This applies equally to the
theme, cart permalinks, Shop Pay / shop.app, the Shop app, connected channels (Google, Meta…)
and carts customers already hold.

### Visible side effects of inventory 0 that are Shopify-native (not theme edits)

The theme code is untouched, but Shopify data changes what Dawn renders. Merchant should
expect and accept:

- PDP: the button is still there, still styled the same, but **disabled** and labelled with
  Dawn's sold-out string (**"Sold out"**). A **"Sold out"** badge appears next to the price
  (`price--sold-out`).
- PDP: Shopify's accelerated checkout / **Shop Pay button hides or disables itself** for an
  unavailable variant (Shopify-controlled; verify in §4).
- Product cards (related products, collections): "Sold out" badge.
- Homepage, header, sticky bar, all marketing CTAs: **unchanged** — they still read "Buy Now"
  and still link to `/products/chillpod`.

Decision point, **default = do nothing**: the word "Sold out" could be changed to
"Coming soon" via *Themes → ⋯ → Edit default theme content → search "Sold out"*
(`products.product.sold_out`). That is a text-only change with no restyle, but it alters the
PDP button label, which the revised plan asks us not to touch. Only do it with explicit
merchant sign-off; note the original value ("Sold out") for revert.

---

## 2. Theme appearance — NO CHANGES

- No Liquid file edits. No `buy-buttons.liquid`, header, homepage or sticky-bar changes.
- No theme settings toggle, no banners, no announcement-bar text, no CTA relabels.
- Do not hide dynamic checkout on the PDP; do not change the Navigation menu.
- The only permitted theme-side item is §3-B, which lives on the Cart template and renders only
  while the product / a line item is unavailable.

The earlier revision of this PR shipped PDP/header/homepage patches; they have been removed.

---

## 3. "Coming soon" message — only at the checkout attempt

How a customer can reach a checkout attempt once inventory is 0: (a) they already had the
item in their cart or a Shop Pay cart, (b) they follow a cart permalink from an ad, email or
this repo's landing page, (c) the Shop app. Fresh visitors never get past the disabled PDP
button. Options in priority order:

### A) Shopify-native sold-out path (preferred — nothing added to the theme)

What the customer sees with qty = 0 and continue-selling off:

| Path | Expected experience (Shopify-controlled) | Verify in §4 |
| --- | --- | --- |
| Cart page `/cart` with the item already in it | Dawn shows the line as usual; pressing **Check out** → Shopify checkout runs an inventory check and shows its **inventory-issue notice** (wording along the lines of *"Some items became unavailable and your cart has been updated"* / *"Sold out"*), removes the line, and cannot proceed to payment. Changing quantity on the cart page returns Dawn's `cart_quantity_error_html` ("You can only add 0 of this item…"). | yes |
| Cart permalink `/cart/67578266419311:1` | Shopify skips the unavailable variant. Expect a redirect to `/cart` (empty, or with the checkout inventory notice) instead of today's Shop Pay handoff. **Payment cannot be reached.** Exact landing page must be confirmed live. | yes |
| Shop Pay / shop.app saved cart | Checkout inventory check blocks; Shop app lists the item as unavailable. | yes |
| Direct `POST /cart/add` | 422 JSON, description *"…is already sold out."* | yes |

Customising that wording to the exact Coming-soon sentence **without touching storefront UI**:

1. **Checkout language (Admin, no theme UI):** Settings → **Checkout** → *Checkout language* →
   **Manage checkout language** (opens the theme language editor, *Checkout & system* tab).
   Search **"unavailable"**, **"sold out"**, **"inventory"**. If the inventory-issue strings are
   exposed there, replace them with *"Coming soon — should be available within the next 30
   days."* Record the originals. **Caveat:** on Shopify's current checkout not every system
   string is editable and this store is not on Plus (no checkout UI extensions / custom
   checkout banners). If the string is not exposed, fall through to B.
2. **Cart quantity error (Dawn, translation only):** Edit default theme content → search
   *"You can only add"* (`sections.cart.cart_quantity_error_html`). It fires only when a
   customer changes quantity of an unavailable line on the cart page. Optional; text-only;
   record the original.
3. **Checkout "additional scripts" / order-status scripts** — not usable: they only run on the
   thank-you / order-status page, which is never reached. Do not attempt.

### B) Minimal theme addition, cart template only (fallback if A's wording can't be edited)

Use `theme-patches/dawn/cart-only/coming-soon-cart-notice.liquid`:

1. Theme editor → template dropdown → **Cart** → **Add section** → **Custom Liquid** → paste
   the file's contents → drag it above *Cart items* → **Save**.
2. It renders **only on `/cart`**, and **only while** `all_products['chillpod'].available ==
   false` **or** a line item's variant is unavailable. The moment inventory is restored it
   outputs nothing. No code files are modified; the section is stored in that theme's
   `templates/cart.json`.
3. It does not block anything; it explains. Text: *"Coming soon — should be available within
   the next 30 days."* plus one reassurance line ("Nothing has been charged").

Boundaries: never place a Custom Liquid section on the Home page, Product template, header or
footer groups. Do not edit `main-cart-items.liquid` / `main-cart-footer.liquid` directly — the
editor-added section is enough and is removable with one click.

### C) Rejected

Storefront-wide announcement bars, Coming Soon banners on PDP/homepage, replacing or relabelling
Buy Now / Get iChillPod CTAs, hiding Shop Pay / dynamic checkout, `coming_soon_mode` theme
settings, header menu relabels, password page, redirects. **Not to be applied.** This also
covers this repo's landing page: its Buy now links stay pointed at the cart permalink, which
after §1 lands on the cart (where A/B message the customer) instead of Shop Pay.

---

## 4. Verification checklist (run right after §1, then again if §3 was applied)

Hard stop:

- [ ] `curl -s https://ichillpod.com/products/chillpod.js | grep -o '"available":[a-z]*' | head -1` → `"available":false`
- [ ] `curl -s -o /dev/null -w '%{http_code}\n' -X POST -d 'id=67578266419311&quantity=1' https://ichillpod.com/cart/add.js` → **422**
- [ ] Private window → `https://ichillpod.com/cart/67578266419311:1` → **no payment / Shop Pay screen reachable**; note where it lands (`/cart` or checkout inventory notice). Each try may leave an empty abandoned checkout in Admin — harmless.
- [ ] Same via `https://ichillpod.myshopify.com/cart/67578266419311:1` (301 → same).
- [ ] Browser that already had the item in cart → `/cart` → **Check out** → checkout shows inventory notice, cannot pay.
- [ ] Shop app / shop.app: item unavailable.
- [ ] Admin → Orders: no new orders after the change (spot-check over the first day).

Storefront unchanged (this is a *negative* check):

- [ ] Homepage hero, featured CTA, FAQ CTA, sticky bar: still read **Buy Now** and link to `/products/chillpod`. Header still "Buy Now".
- [ ] PDP layout identical; button present but disabled with Shopify's sold-out label; price **$29.95** still shown; Shop Pay button hidden/disabled by Shopify.
- [ ] Theme code files unchanged (Themes → ⋯ → Edit code → no recent edits; or compare with the duplicate).

Message (whichever of A/B was used):

- [ ] The sentence *"Coming soon — should be available within the next 30 days."* appears on the cart / checkout attempt path and **nowhere else** (view-source search on homepage and PDP: 0 hits).
- [ ] With B: `/cart` with an empty cart still shows the notice while inventory is 0 (because the product is unavailable) — this is the permalink landing case.

---

## 5. Revert — exact steps

1. **Inventory** (Admin → Products → iChillPod → Inventory):
   - Tracking was **Off** before (state recorded in §0): untick **Track quantity** → Save →
     variant is unlimited again. *(Or keep tracking on and enter the real stock count — a
     deliberate change; record it.)*
   - If §0 recorded a tracked quantity: enter it back for each location; re-tick *Continue
     selling when out of stock* only if it was on before.
   - Confirm `…/products/chillpod.js` → `"available":true`; PDP button active; Shop Pay back.
2. **Message clean-up:**
   - A-1 / A-2: restore the original checkout / cart strings you recorded.
   - B: Theme editor → Cart → remove the *Custom Liquid* section → Save. (It already renders
     nothing once inventory is back, so the order of 1 and 2 does not matter.)
   - Sold-out translation, if the merchant approved changing it: set back to "Sold out".
3. **Storefront:** nothing to revert — it was never changed.
4. **This repo:** nothing to revert — `index.html` is unchanged in this PR.
5. Re-run §4 in reverse: permalink reaches checkout again; place a test order if desired
   (Admin → Settings → Payments → test mode, or cancel/refund a real $29.95 order).

---

## 6. Irreversibility / risk flags — read before applying live

- **Nothing here is irreversible** when done as written. Deliberately excluded because they are
  destructive or hard to undo: deleting product / variants / media, price changes, URL
  redirects, unpublishing channels, storefront password, disabling payment providers.
- **Enabling Track quantity** is reversible, but while on Shopify decrements stock on any
  future sale; on revert either turn it off again or enter the correct count.
- **Orders are blocked for everyone**, including staff testing — use Admin draft orders if you
  must sell manually during the window.
- **Abandoned-checkout recovery emails / Flow / Klaviyo** may keep sending "complete your
  order" links whose checkout will fail. Pause them for the window; emails already sent can't
  be recalled.
- **Channel propagation** (Google & YouTube, Meta, Shop): availability changes can take hours in
  both directions.
- **Checkout language edits (A-1)** apply store-wide to every checkout string you change —
  only change the inventory-issue strings, nothing else, and record originals.
- **Custom Liquid section (B)** is stored in `templates/cart.json` of the theme you edit only;
  if a different theme is published later it will not carry over (harmless).
- A theme duplicate taken before §3-B is the one-click restore for the Cart template.
