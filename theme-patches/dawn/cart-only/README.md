# Cart-only Coming Soon notice (optional)

Per the merchant's revised decision, **the Dawn storefront is not changed**: no Coming Soon
banners, no CTA or label changes, no hiding of Buy Now / Shop Pay, no PDP / homepage / header
edits. The only allowed theme-side messaging is something a customer meets **at the cart /
checkout attempt**, and only if Shopify's native wording (see the runbook, §3-A) is not enough.

This folder contains exactly one such option:

| File | Applied where | Touches code files? | Shows on |
| --- | --- | --- | --- |
| `coming-soon-cart-notice.liquid` | Theme editor → **Cart** template → *Add section* → **Custom Liquid** → paste | **No** (stored in `templates/cart.json` of that theme only) | `/cart` page only, and only while the product / a line item is unavailable |

It renders the sentence **"Coming soon — should be available within the next 30 days."** and is
self-hiding: once inventory is restored (`product.available == true`, no unavailable line
items) it outputs nothing. Removing the section from the Cart template in the editor is the
full clean-up.

Nothing in this folder is deployed by this repository. It does not block orders; the inventory
hard stop in Shopify Admin does (runbook §1).

Rejected and deliberately **not** provided anymore: `buy-buttons.liquid` patches, header
menu relabels, homepage / sticky-bar CTA swaps, a `coming_soon_mode` theme setting, cart /
drawer checkout-button hiding. Those altered storefront appearance.
