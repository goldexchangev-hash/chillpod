# Dawn 16 theme patches — Coming Soon mode

**These files are NOT deployed by this repo.** This repository is a static Render landing
page. Nothing in `theme-patches/` reaches Shopify unless a human pastes it into
**Shopify Admin → Online Store → Themes → … → Edit code** on the live theme
("Dawn — payment icons preview", Dawn schema **16.0.0**, theme id `188025995375`,
shop `yz0m1m-ru.myshopify.com` / `ichillpod.com`).

Read `docs/COMING_SOON_DISABLE_ORDERS.md` first. These patches are **Layer 2 (messaging)**.
They hide buy buttons and show "Coming Soon / Availability coming soon". They do **not**
block orders — only **Layer 1 (inventory = 0 in Admin)** does.

## Recommended way to apply (fully reversible)

1. Themes → live theme → **⋯ → Duplicate**. Rename the copy e.g. `Dawn — coming soon`.
2. Apply the patches below to the **copy** via Edit code.
3. **Preview** the copy; run the verification checklist from the runbook.
4. **Publish** the copy. Revert later = **Publish** the original theme again (one click),
   or just untick *Theme settings → Coming Soon mode* on the published copy.

## Files

| File in this folder | Target in Shopify Edit code | Required? | What it does |
| --- | --- | --- | --- |
| `config/settings_schema.coming-soon.json` | `config/settings_schema.json` — **append** the object as a new array element (do not replace the file) | Required | Adds *Theme settings → Coming Soon mode*: `coming_soon_mode` checkbox (**default: true**) + editable label / supporting line / note text. |
| `snippets/coming-soon-notice.liquid` | `snippets/` → Add a new snippet named `coming-soon-notice` | Required | Renders the Coming Soon block (`block` layout for the PDP, `inline` for pills). |
| `snippets/buy-buttons.liquid` + `buy-buttons.diff` | `snippets/buy-buttons.liquid` | Required | PDP: when the toggle is on, replaces `<product-form>` (Add to cart / "Buy Now" submit **and** `{{ form \| payment_button }}` = Shop Pay / accelerated checkout) and pickup availability with the notice. Full file is stock Dawn 16.0.0 + the diff; if your file has local edits, apply the diff only. |
| `sections/chillpod-custom-sections.md` | `sections/chillpod-hero.liquid`, `chillpod-featured-cta.liquid`, `chillpod-faq.liquid`, `chillpod-sticky-bar.liquid` | Required (labels) | Pattern for the store's custom homepage / sticky-bar "Buy Now" CTAs whose source is only in Shopify. Check editor settings first. |
| `header-optional.diff` | `snippets/header-drawer.liquid`, `header-mega-menu.liquid`, `header-dropdown-menu.liquid` | Optional | Relabels the `buy-now` menu item (`HeaderDrawer-buy-now`, `HeaderMenu-buy-now`) to Coming Soon while the toggle is on. **Simpler alternative with no code:** Admin → Online Store → Navigation → main menu → rename "Buy Now" → "Coming Soon" (keep link `/products/chillpod`). |
| `cart-optional.diff` | `sections/main-cart-footer.liquid`, `snippets/cart-drawer.liquid`, `snippets/cart-notification.liquid` | Optional | Hides the cart page / drawer / add-to-cart-notification **Check out** buttons and `content_for_additional_checkout_buttons` while the toggle is on. Cosmetic: with inventory at 0 checkout already fails server-side. |

## Zero-code fallback (if you don't want to touch Liquid)

1. Theme editor → **Products → Default product** → *Product information* → **Buy buttons**
   block → untick **Show dynamic checkout buttons** (removes Shop Pay / accelerated checkout).
2. Themes → live theme → **⋯ → Edit default theme content** → search `Sold out` → set
   `products.product.sold_out` to `Coming Soon` (also relabels the price badge and product
   cards). Optionally set the PDP button string (currently rendered as "Buy Now") the same way.
3. Navigation → rename "Buy Now" → "Coming Soon".
4. Editor → change the custom sections' button labels / hide the sticky bar.
5. Still do Layer 1 (inventory 0). Sold-out + Coming Soon text is what customers see.

## Notes / gotchas

- `default: true` on `coming_soon_mode` means the moment the schema is saved the site is in
  Coming Soon mode (that is the campaign intent). Once you Save in the editor the value is
  persisted in `config/settings_data.json`; unticking and saving reverts.
- The product has a single variant (`Default Title`, id `67578266419311`), so Dawn's
  variant-change JS (`assets/product-info.js`) never needs to re-render the submit button.
  If more variants are added later, the JS tolerates a missing `ProductSubmitButton-*`
  element (treats it as disabled).
- Do **not** edit `assets/*.js` or `layout/theme.liquid` for this — not needed.
- Do **not** delete images/variants, change `$29.95`, add redirects, or password the store.
