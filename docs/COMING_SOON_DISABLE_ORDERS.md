# Ordering paused on ichillpod.com — inventory hard stop + "Sold out" → "Coming soon" (reversible)

**Nothing in this repo changes the live store.** This document tells a human what to do in
**Shopify Admin on the live Dawn theme**. Merging this PR does not touch ichillpod.com.

## Current live state (observed read-only 2026-09-27, after the merchant's Admin changes)

| | |
| --- | --- |
| Live storefront / shop | https://ichillpod.com — `yz0m1m-ru.myshopify.com` (`ichillpod.myshopify.com` 301s to it) |
| Live theme | **Dawn — payment icons preview**, Dawn schema **16.0.0**, theme id `188025995375`, role `main`, cart type *notification* (no drawer), English only |
| Product / variant | `iChillPod - No-Power Phone Cooler for Saunas`, handle `chillpod`, product `15554226356335`, variant **`67578266419311`** (`Default Title`, single variant), **$29.95**, status Active |
| **Inventory hard stop** | **IN PLACE.** `inventory_management: "shopify"` (Track quantity on), `available: false`. Merchant set quantity **0**. Keep *Continue selling when out of stock* **off** — that is what makes `available` false. **Do not undo.** |
| Sold-out label | `products.product.sold_out` is **already rendered as "Coming soon "** (note the trailing space) on the PDP button, the price badge and collection cards. `Sold out` no longer appears in the homepage, PDP, cart or `/collections/all` HTML. |
| Everything else | Buy Now / Get iChillPod CTAs, header menu, homepage sections, sticky bar, Shop Pay markup: **unchanged**. PDP button is present, same style, `disabled`. |
| Before the change | Inventory was **not tracked** (unlimited). Record this: revert = turn *Track quantity* off again (or enter the real count). |

Copy to use: short label **Coming soon**; longer notice (cart/checkout attempt only, optional)
**"Coming soon — should be available within the next 30 days."**

---

## 1. Hard stop — keep as is (Shopify Admin)

Already applied by the merchant. To re-check or re-apply:

Admin → **Products** → *iChillPod* → **Inventory** card: *Track quantity* **on**, *Continue
selling when out of stock* **off**, *Available* **0** at every location → Save.

Effects (Shopify-enforced, theme-independent): `POST /cart/add` → 422 "sold out"; cart
permalinks skip the variant; Shopify checkout refuses the line item; Shop app / channels show
unavailable; the PDP submit button is `disabled` and Shopify hides/disables the accelerated
checkout button for an unavailable variant.

Do **not**: set to Draft, unpublish from any channel, delete variant/media, change price or
compare-at, add redirects, password the store, disable Shop Pay or payment providers.

---

## 2. Rename "Sold out" → "Coming soon" — first choice: theme content (no Liquid, no layout)

Path: Admin → **Online Store → Themes** → live theme → **⋯ → Edit default theme content**
(older Admin: *Edit languages*). Use the search box at the top; each hit shows the key path.
Changes save per theme; nothing else in the theme moves.

### Keys to set (Dawn 16.0.0 `locales/en.default.json`)

| # | Key (search term) | Dawn default | Where it renders | Set to | Status / notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `products.product.sold_out` (**"Sold out"**) | `Sold out` | PDP submit button when unavailable (`snippets/buy-buttons.liquid`); price badge `price__badge-sold-out` (`snippets/price.liquid`); product-card badges and quick-add buttons (`snippets/card-product.liquid` — related products, collections, search); quick-order rows; JS `window.variantStrings.soldOut` (`layout/theme.liquid`) | **Coming soon** | **Already done on live**, but the saved value has a **trailing space** (`Coming soon `). Re-open the field, delete the trailing space, Save. |
| 2 | `sections.cart.cart_quantity_error_html` (**"You can only add"**) | `You can only add {{ quantity }} of this item to your cart.` | Cart page line-item error when a customer changes the quantity of a line whose variant is unavailable (`assets/cart.js` → `cartStrings.quantityError`) | **Coming soon — should be available within the next 30 days. This item can't be ordered yet.** | Optional; the only Dawn *cart* string a blocked customer can trigger. Dropping `{{ quantity }}` is fine (Dawn does a no-op replace). Record the original. |
| 3 | `products.product.inventory_out_of_stock` (**"Out of stock"**) | `Out of stock` | Only if the *Inventory status* block is ever added to *Product information* — **not on the live PDP today** | **Coming soon** | Optional / future-proofing. |
| 4 | `products.product.variant_sold_out_or_unavailable` | `Variant sold out or unavailable` | Screen-reader text on variant pickers — product has a single variant, **not rendered** | leave, or `Variant coming soon or unavailable` | Optional. |
| 5 | `products.product.unavailable` / `products.product.value_unavailable` | `Unavailable` / `{{ option_value }} - Unavailable` | Only when a variant doesn't exist for a selection — **not the sold-out case**; leave | leave | Changing these would mislabel a different state. |
| 6 | `products.product.pickup_availability.unavailable` | `Couldn't load pickup availability` | Pickup widget error, unrelated | leave | — |

Do **not** change `products.product.add_to_cart` or any button/CTA label — those are the
in-stock state and must come back untouched on revert. (Note: the live PDP rendered
**"Buy Now"** while in stock although the locale default is "Add to cart", so the live
`buy-buttons.liquid` or `main-product.liquid` carries a local label edit; it does not affect
the sold-out branch, which correctly reads the locale key — leave it alone.)

### Checkout (Shopify-hosted, outside the theme)

If a customer with an old cart / Shop Pay cart / permalink reaches checkout, Shopify shows its
own inventory notice (wording along the lines of *"Some items became unavailable and your cart
has been updated"* / *"Sold out"*) and removes the line. To align it:

Admin → **Settings → Checkout** → *Checkout language* → **Manage checkout language** → search
**"sold out"**, **"unavailable"**, **"no longer available"**, **"inventory"**. If exposed, set the
inventory-issue strings to *"Coming soon — should be available within the next 30 days."* and
record the originals. **Caveat:** Shopify's current checkout does not expose every system
string and this store is not on Plus (no checkout UI extensions). If the strings are not
editable, accept the native wording — the storefront itself no longer says "Sold out".
Order-status "additional scripts" cannot help (they run only after an order).

### Multiple languages

Only English (`en`) is published (buyer locale `en`). If other languages are added later,
repeat #1 (and #2) for each locale in **Edit default theme content → language selector**
or the *Translate & Adapt* app.

---

## 3. Fallback — minimal Liquid, only if a "Sold out" string is hard-coded

Stock Dawn 16.0.0 has **no hard-coded "Sold out"** in rendered Liquid (the only occurrence is a
code comment in `snippets/price.liquid`). Every surface uses `products.product.sold_out`.
The live theme confirms this: after the content edit, "Sold out" is absent from all fetched
pages.

Only if a future scan finds a literal "Sold out" (Edit code → search box → `Sold out`): change
**only the text** to `Coming soon` — do not touch markup, classes, `disabled` attributes,
`{{ form | payment_button }}`, or block structure. Duplicate the theme first so the original
file is one click away. Not needed today.

---

## 4. Optional — longer notice on the cart page only

`theme-patches/dawn/cart-only/coming-soon-cart-notice.liquid` renders *"Coming soon — should be
available within the next 30 days."* on **`/cart` only**, and **only while** the product / a
line item is unavailable (self-hides once inventory returns). Applied via *Theme editor → Cart
template → Add section → Custom Liquid → paste* — no code files. It is **not** a storefront
banner and is **not** required; the default is to skip it unless the merchant wants the longer
sentence where a permalink or old cart lands. Never add it to Home, Product, header or footer.

Rejected (do not apply): Coming Soon banners on PDP/homepage, announcement-bar text, CTA
replacements or relabels, hiding Buy Now / Shop Pay / dynamic checkout beyond what sold-out
already does, theme setting toggles, header menu renames, redirects, password page.

---

## 5. Verification

Hard stop (already true on 2026-09-27; re-run any time):

- [ ] `curl -s https://ichillpod.com/products/chillpod.js | grep -o '"available":[a-z]*' | head -1` → `"available":false`
- [ ] `curl -s -o /dev/null -w '%{http_code}\n' -X POST -d 'id=67578266419311&quantity=1' https://ichillpod.com/cart/add.js` → `422`
- [ ] Private window → `https://ichillpod.com/cart/67578266419311:1` → no payment / Shop Pay screen reachable (expect `/cart` or Shopify's checkout inventory notice). May leave an empty abandoned checkout in Admin — harmless.
- [ ] Old cart: `/cart` → **Check out** → Shopify inventory notice, cannot pay.
- [ ] Admin → Orders: no new orders since the change.

Label:

- [ ] `curl -s https://ichillpod.com/products/chillpod | grep -c 'Sold out'` → `0`; same for `/`, `/cart`, `/collections/all`.
- [ ] PDP button reads **Coming soon** (no trailing space: `grep -o 'Coming soon[^<]*<' ` shows `Coming soon<`), still `disabled`, same style; price badge reads **Coming soon**; **$29.95** still shown.
- [ ] Collection / related-product cards: badge **Coming soon**.
- [ ] If #2 applied: on `/cart` with the item present, change quantity → error text is the Coming-soon sentence.
- [ ] If checkout language edited: old-cart checkout shows the Coming-soon sentence.

Storefront otherwise unchanged (negative check):

- [ ] Homepage hero / featured CTA / FAQ CTA / sticky bar still read **Buy Now**; header still **Buy Now**; all still link to `/products/chillpod`.
- [ ] Edit code shows no modified Liquid/JSON files from this work (only theme content / translations changed).

---

## 6. Revert — exact steps

1. **Inventory** — Admin → Products → iChillPod → Inventory:
   - Prior state was **not tracked**: untick **Track quantity** → Save (unlimited again). Or keep
     tracking and enter the real stock count per location — a deliberate change; note it.
   - Re-tick *Continue selling when out of stock* **only** if it was on before (it was not
     applicable — tracking was off).
   - Check `…/products/chillpod.js` → `"available":true`; PDP button active ("Buy Now"), Shop Pay
     visible again.
2. **Theme content** — Edit default theme content:
   - `products.product.sold_out` → **Sold out**
   - `sections.cart.cart_quantity_error_html` → **You can only add {{ quantity }} of this item to your cart.** (if changed)
   - `products.product.inventory_out_of_stock` → **Out of stock** (if changed)
   - `products.product.variant_sold_out_or_unavailable` → **Variant sold out or unavailable** (if changed)
   - Checkout language strings → the originals you recorded (if changed)
   Once inventory is back these strings are not rendered anyway, so order of 1 and 2 doesn't
   matter — but restore them so the theme is clean for the next sold-out event.
3. **Optional cart notice** (§4) — Theme editor → Cart → remove the Custom Liquid section → Save.
4. **Storefront / this repo** — nothing to revert; neither was changed.

---

## 7. Irreversibility / risk flags — read before applying live

- **The string swap is reversible** (per-theme content edit; originals listed in §6). **Inventory
  changes are reversible.** Nothing in this plan is destructive.
- Content edits are stored **on the theme you edit**. Publishing a different theme (or a fresh
  duplicate made *before* the edit) drops them — harmless, but re-apply if that happens.
- **Track quantity on** means Shopify will decrement stock on any future sale; on revert turn it
  off again or enter the correct count.
- **Orders are blocked for everyone**, including staff; use Admin draft orders for manual sales.
- **Abandoned-checkout / marketing automations** may keep sending "complete your order" links
  that will fail — pause them for the window; sent emails can't be recalled.
- **Channel propagation** (Shop, Google & YouTube, Meta) lags by hours in both directions.
- **Checkout language edits apply store-wide** — change only the inventory-issue strings.
- Excluded on purpose: deleting product/variants/media, price changes, redirects, unpublishing,
  password page, payment-provider changes.
