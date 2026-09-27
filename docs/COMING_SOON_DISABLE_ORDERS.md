# Coming Soon — temporarily disable ordering on ichillpod.com (reversible)

**Status:** runbook + copy-paste theme patches. **Nothing here changes the live store by
itself.** Merging this PR only updates the static Render landing page in this repo. The live
Shopify storefront is blocked from taking orders **only after a human performs the Shopify
Admin steps (Layer 1) and the Dawn theme steps (Layer 2) below.**

| | |
| --- | --- |
| Live storefront | https://ichillpod.com (Shopify Online Store) |
| Shop | `yz0m1m-ru.myshopify.com` (admin handle `ichillpod`; `ichillpod.myshopify.com` 301s to `ichillpod.com`) |
| Live theme | **Dawn — payment icons preview**, Dawn schema **16.0.0**, theme id `188025995375`, role `main` |
| Product | `iChillPod - No-Power Phone Cooler for Saunas`, handle `chillpod`, product id `15554226356335` |
| Variant | `Default Title`, variant id **`67578266419311`**, price **$29.95** (single variant) |
| Cart permalink to block | `https://ichillpod.com/cart/67578266419311:1` (also reachable via `ichillpod.myshopify.com/cart/67578266419311:1`) |
| This repo | `goldexchangev-hash/chillpod` — static `index.html` deployed on Render. **Not** the Dawn theme. |

Facts above were read from the public storefront on **2026-09-27** (`/products/chillpod.js`,
page HTML, `Shopify.theme`). Re-check them before applying if time has passed.

Customer-facing copy (use exactly unless the merchant edits):

- Button / badge: **Coming Soon**
- Supporting line: **Availability coming soon**
- Optional note: **We're not taking orders right now. Check back soon.**

---

## 0. Before you touch anything — record the current state

Write these down (in the PR, a ticket, or the Admin timeline) so revert is exact.

| Item | Where to look | Value observed 2026-09-27 | Value at time of applying |
| --- | --- | --- | --- |
| Inventory tracking on the variant | Admin → Products → iChillPod → Inventory card → *Track quantity* | **Off** (`inventory_management: null` → unlimited, "available: true") | |
| Inventory quantity | same card | n/a (not tracked) | |
| *Continue selling when out of stock* | same card | n/a (only shown when tracking is on) | |
| Product status | Admin → Products → iChillPod | Active | |
| Sales channels on product | same page → Publishing | Online Store (+ whatever else is listed — do not change) | |
| Price / compare-at | Variant | $29.95 / (check) | |
| PDP *Show dynamic checkout buttons* | Theme editor → Products → Product information → Buy buttons block | **On** (Shop Pay accelerated checkout renders) | |
| PDP button label | rendered `<button name="add">` text | "Buy Now" (Dawn default is "Add to cart" → a translation or snippet edit already exists) | |
| Header menu item | Admin → Online Store → Navigation → main menu | "Buy Now" → `/products/chillpod` (ids `HeaderMenu-buy-now`, `HeaderDrawer-buy-now`) | |
| Homepage CTAs | custom sections `chillpod-hero`, `chillpod-featured-cta`, `chillpod-faq` | "Buy Now", "Buy Now", "Buy Now — $29.95" → all `/products/chillpod` | |
| Sticky bar | footer group section `chillpod-sticky-bar` (all pages) | "Buy Now" → `/products/chillpod`, shows $29.95 + Patent Pending | |
| Cart permalink behaviour | `curl -sI https://ichillpod.com/cart/67578266419311:1` | **302 → `shop.app/checkout/...shoppay`** (goes straight to Shop Pay checkout) | |

Also **Duplicate the live theme** (Themes → ⋯ → Duplicate) before any code edit. Publishing
the untouched original is the one-click theme revert.

---

## 1. Layer 1 — Hard stop: inventory = 0 (Shopify Admin, REQUIRED)

Theme edits cannot block `/cart/add`, cart permalinks, Shop Pay deep links, the Shop app,
or carts customers already have. Shopify's inventory gate is the only real stop.

**Gotcha specific to this store:** the variant is currently **not tracked**
(`inventory_management: null`). Setting a quantity does nothing until tracking is on.
Untracked = unlimited stock.

1. Shopify Admin → **Products** → *iChillPod - No-Power Phone Cooler for Saunas*.
2. **Inventory** card → tick **Track quantity**.
3. Make sure **Continue selling when out of stock** is **unticked**.
4. Set **Available** quantity to **0** for every location listed (there may be more than one;
   all must be 0). If the product has *Shop location* / *Shopify Fulfillment Network* rows, set
   those to 0 too.
5. **Save.**
6. Do **not**: set the product to Draft, unpublish it from Online Store or any channel, remove
   the variant, delete media, change the price / compare-at, archive the product, add URL
   redirects, or password-protect the store. All of those are out of scope and some (delete)
   are irreversible.

Expected effect within about a minute (CDN): `product.available == false`; the PDP button
renders disabled with the `products.product.sold_out` string; `POST /cart/add` returns 422
(`"sold out"`); a cart permalink lands on the cart/checkout with a "sold out / no longer
available" error instead of the Shop Pay payment sheet; Shop app and any connected channels
show the item unavailable.

Optional belt-and-braces (also reversible): Admin → Settings → **Checkout** → nothing needs
changing. Do **not** disable Shop Pay or payment providers — that affects future revert and
can trigger provider re-verification.

---

## 2. Layer 2 — Messaging: "Coming Soon" instead of "Sold out" (Dawn theme, REQUIRED for copy)

After Layer 1 the store says **Sold out**. This layer swaps that for **Coming Soon /
Availability coming soon** and removes purchase-looking UI. Two ways; pick one. Work on the
**duplicated** theme, preview, then publish.

### 2A. Preferred — theme setting toggle `coming_soon_mode` (copy-paste from `theme-patches/dawn/`)

Files live in [`theme-patches/dawn/`](../theme-patches/dawn/README.md). Apply in **Edit code**:

1. **Setting.** Open `config/settings_schema.json`. Append the object from
   `theme-patches/dawn/config/settings_schema.coming-soon.json` (drop its `_comment` key) as a
   new element at the end of the top-level array (add the comma). Save. A **Coming Soon mode**
   group now appears under *Theme settings*; `coming_soon_mode` **defaults to true**.
2. **Snippet.** Snippets → *Add a new snippet* → `coming-soon-notice` → paste
   `theme-patches/dawn/snippets/coming-soon-notice.liquid`. Save.
3. **PDP buy buttons.** Open `snippets/buy-buttons.liquid`. Compare with the stock Dawn 16.0.0
   version; if identical, replace the content with `theme-patches/dawn/snippets/buy-buttons.liquid`.
   If it has local edits (e.g. the "Buy Now" label), apply only the lines in
   `theme-patches/dawn/buy-buttons.diff` (two small insertions). This hides the
   `<product-form>` — the Add to cart / Buy Now submit **and** `{{ form | payment_button }}`
   (Shop Pay / accelerated checkout) — and the pickup-availability widget, and renders the
   Coming Soon block in their place. Price, title, description, media, share stay untouched.
4. **Header "Buy Now".** Either (no code) Admin → Online Store → **Navigation** → main menu →
   rename **Buy Now → Coming Soon**, keep the link `/products/chillpod` (informational is OK,
   never a `/cart/…` or checkout URL); **or** apply `theme-patches/dawn/header-optional.diff`
   to `snippets/header-drawer.liquid`, `header-mega-menu.liquid`, `header-dropdown-menu.liquid`
   so the `buy-now` item is relabelled only while the toggle is on.
5. **Homepage + sticky bar CTAs.** Follow
   `theme-patches/dawn/sections/chillpod-custom-sections.md` for
   `sections/chillpod-hero.liquid`, `chillpod-featured-cta.liquid`, `chillpod-faq.liquid`,
   `chillpod-sticky-bar.liquid`. Check the theme editor for a label setting first; otherwise wrap
   the anchor in `{% if settings.coming_soon_mode %}{% render 'coming-soon-notice', layout: 'inline', href: '/products/chillpod' %}{% else %}…{% endif %}`.
   Search every section for `cart/` and `checkout` and remove any such destinations while the
   toggle is on (none were found on the live homepage on 2026-09-27).
6. **Cart (optional).** Apply `theme-patches/dawn/cart-optional.diff` to
   `sections/main-cart-footer.liquid`, `snippets/cart-drawer.liquid`,
   `snippets/cart-notification.liquid` to hide the **Check out** buttons and
   `content_for_additional_checkout_buttons` while the toggle is on. Cosmetic — inventory 0
   already makes checkout fail.
7. **Sold-out strings (recommended).** Themes → ⋯ → **Edit default theme content** → search
   `Sold out` → set `products.product.sold_out` to **Coming Soon**. This covers the PDP price
   badge (`price__badge-sold-out`), product cards / related products, and the JS fallback
   string used when a variant becomes unavailable. Note the original value ("Sold out").
8. **Preview** the duplicated theme → run section 4 → **Publish**.

### 2B. Fallback — no new settings, editor + translations only

1. Theme editor → **Products → Default product** → *Product information* → **Buy buttons**
   block → untick **Show dynamic checkout buttons** (removes Shop Pay / accelerated checkout).
   Stored in `templates/product.json`; reversible by re-ticking.
2. **Edit default theme content**: `products.product.sold_out` → **Coming Soon**. The button
   is disabled by Layer 1, so it reads "Coming Soon" and does nothing. Optionally set the
   *Add to cart* string (currently rendering "Buy Now") to "Coming Soon" too.
3. Navigation → rename **Buy Now → Coming Soon**.
4. Theme editor → change the custom sections' button labels to **Coming Soon** (or hide the
   sticky bar with the eye icon). Record old labels.
5. Add the line **Availability coming soon** via a *Text* block in *Product information* under
   the price (editor → Add block → Text). Remove the block on revert.

### What NOT to do in Layer 2

- No interstitials, no meta refresh, no 301/302 away from `/products/chillpod` or the domain.
- Don't change `$29.95` or compare-at, don't touch product media, variants, SEO fields.
- Don't edit `assets/*.js`; nothing here requires it.
- Don't enable the storefront password page (that blocks browsing, not just buying).

---

## 3. Other places orders can still originate — check, don't change

| Surface | What inventory = 0 does | Action |
| --- | --- | --- |
| **Shop app / Shop Pay** (`shop.app`) | Item shows unavailable; existing Shop Pay carts fail at checkout | none |
| Google & YouTube / Meta / TikTok channels (if installed) | Availability syncs to "out of stock" (can take up to a few hours) | none; do not unpublish |
| **Buy Button** embeds / this repo's `index.html` permalinks | Permalink lands on cart with sold-out error | this PR replaces the Render page CTAs with Coming Soon (section 6) |
| Abandoned checkout recovery emails / Shopify Flow / Klaviyo etc. | Would still email "complete your order" links | consider pausing automations for the campaign; note what you paused |
| Draft orders created by staff | Admin can still sell untracked/negative stock manually | intentional; leave |
| Discount codes / automatic discounts | Unaffected | leave |

---

## 4. Verification checklist (run after publishing the theme, on desktop + phone)

Layer 1 (hard stop):

- [ ] `curl -s https://ichillpod.com/products/chillpod.js | grep -o '"available":[a-z]*' | head -1` → `"available":false`
- [ ] `curl -s -o /dev/null -w '%{http_code}\n' -X POST -d 'id=67578266419311&quantity=1' https://ichillpod.com/cart/add.js` → **422**
- [ ] Open **`https://ichillpod.com/cart/67578266419311:1`** in a private window → must **not** reach a payment/Shop Pay screen; expect cart or checkout with "sold out / unavailable" error and **no way to pay**. (Each visit may create an empty abandoned checkout record — harmless.)
- [ ] Same for `https://ichillpod.myshopify.com/cart/67578266419311:1` (301 → same result).
- [ ] Old cart: in a browser that already had the item in cart, open `/cart` → item flagged unavailable / quantity error; **Check out** cannot complete.
- [ ] Shop app search "iChillPod" → unavailable.

Layer 2 (messaging):

- [ ] PDP `/products/chillpod`: no Add to cart / Buy Now / Shop Pay / accelerated checkout button; **Coming Soon** + **Availability coming soon** visible; price **$29.95** still shown; images, description, share unchanged.
- [ ] Homepage: hero, featured CTA card, FAQ CTA all read **Coming Soon**; no path to checkout.
- [ ] Header desktop + mobile drawer: menu item reads **Coming Soon**; links to `/products/chillpod` or nothing.
- [ ] Sticky bar (all pages, mobile): **Coming Soon**, price still visible, no checkout link.
- [ ] `/cart` and cart drawer: no working Check out button (if cart patch applied) — otherwise checkout errors on sold-out.
- [ ] Nowhere on the site does "Sold out" appear (if translations edited) — search page source for `Sold out`.
- [ ] Footer social links, policy pages, contact form untouched.
- [ ] Theme editor still loads without schema errors (`settings_schema.json` valid JSON).
- [ ] Render landing page (this repo, after merge/deploy): no `/cart/` links, CTAs read Coming Soon.

---

## 5. Revert — exact steps (in this order)

1. **Restore inventory first** (Admin → Products → iChillPod → Inventory):
   - If tracking was **Off** before (the state observed 2026-09-27): untick **Track quantity**
     → Save. The variant is unlimited again. (Alternatively leave tracking on and enter the real
     stock count — a deliberate change; note it.)
   - If tracking was On before: set quantity back to the recorded number; re-tick *Continue
     selling when out of stock* only if it was on before.
   - Confirm `…/products/chillpod.js` shows `"available":true`.
2. **Theme toggle off:** Theme editor → Theme settings → **Coming Soon mode** → untick → Save.
   All `{% if settings.coming_soon_mode %}` patches (PDP buy buttons + Shop Pay, header label,
   custom sections, cart buttons) return to normal instantly. Or republish the untouched
   duplicate of the original theme.
3. **Translations:** Edit default theme content → `products.product.sold_out` back to
   **Sold out** (and any other string you changed).
4. **Navigation:** rename **Coming Soon → Buy Now** if you renamed it.
5. **Editor-level changes:** restore custom-section button labels, unhide the sticky bar,
   remove any "Availability coming soon" text block, re-tick *Show dynamic checkout buttons*
   if you used fallback 2B.
6. **Automations:** resume anything paused in section 3.
7. **This repo:** revert the `index.html` commit from this PR (or restore the four
   `https://ichillpod.myshopify.com/cart/67578266419311:1` links listed in the HTML comment at
   the bottom of `index.html`) and deploy on Render.
8. Re-run: PDP shows Buy Now + Shop Pay; permalink reaches checkout; test order if desired.

Optional cleanup after the campaign: leave the `coming_soon_mode` setting and snippet in place
(off) for reuse, or remove them from the theme copy.

---

## 6. What this PR changes in this repo (Render landing page — parity only)

- `index.html`: the four purchase CTAs (header pill, hero, offer card, mobile sticky bar) no
  longer link to the Shopify cart permalink. They render a non-link **Coming Soon** pill
  (`aria-disabled="true"`) with **Availability coming soon** underneath. Prices, payment-icon
  trust row, guarantee copy, FAQ, social/footer are untouched. The original hrefs are kept in
  an HTML comment for revert.
- `README.md`: notes the coming-soon state and links here.

Deploying this repo does **not** affect ichillpod.com's Shopify theme.

---

## 7. Irreversibility / risk notes

- **Nothing in this plan is irreversible** if followed. Risky operations deliberately excluded:
  deleting product/variants/media, changing price, redirects, unpublishing channels, storefront
  password, disabling payment providers.
- Turning **Track quantity on** is reversible, but note that while it is on Shopify will
  decrement stock on any future order — restore the correct count or turn tracking off again.
- Theme code edits are reversible via the duplicated theme; **editor Saves persist** to
  `config/settings_data.json` / `templates/*.json` on that theme only.
- Channel syncs (Google/Meta) may take hours to show "in stock" again after revert.
- Abandoned-checkout emails sent during the campaign cannot be unsent — pause them first.
