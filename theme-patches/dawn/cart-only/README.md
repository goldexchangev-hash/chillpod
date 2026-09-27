# Cart-only Coming soon notice (optional, not required)

The plan for ichillpod.com is: inventory 0 (already in place) + rename the theme content string
`products.product.sold_out` from "Sold out" to **Coming soon** via *Edit default theme content*
(already rendering live; trailing space to trim). See `docs/COMING_SOON_DISABLE_ORDERS.md`.
No Liquid layout edits, no hidden buttons, no marketing banners.

This folder holds one **optional** extra for the longer sentence, if the merchant wants it
where a permalink or an old cart lands:

| File | Applied where | Touches code files? | Shows on |
| --- | --- | --- | --- |
| `coming-soon-cart-notice.liquid` | Theme editor → **Cart** template → *Add section* → **Custom Liquid** → paste | **No** (stored in that theme's `templates/cart.json`) | `/cart` page only, and only while the product / a line item is unavailable |

It renders **"Coming soon — should be available within the next 30 days."** and is self-hiding
once inventory is restored. Removing the section in the editor is the full clean-up.

Not deployed by this repository. Does not block orders (inventory does). Default: skip it.
