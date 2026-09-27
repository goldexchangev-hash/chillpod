# Custom ChillPod sections — Coming Soon pattern

The live homepage (`ichillpod.com`, theme "Dawn — payment icons preview", schema 16.0.0)
renders these **custom** sections that are not part of stock Dawn. Their Liquid source lives
only in the Shopify theme, not in this repo, so they cannot be diffed here. Observed on
2026-09-27 from the public storefront HTML:

| Section file (Edit code → Sections)           | Where it renders                 | Purchase CTA observed                                             |
| --------------------------------------------- | -------------------------------- | ----------------------------------------------------------------- |
| `sections/chillpod-hero.liquid`               | Homepage (`index.json`)          | `<a class="chillpod-hero__cta button" href="/products/chillpod">Buy Now</a>` |
| `sections/chillpod-featured-cta.liquid`       | Homepage (`index.json`)          | `<a class="chillpod-featured-cta__card" href="/products/chillpod" aria-label="Buy Now">` wrapping `<span class="chillpod-featured-cta__btn">Buy Now</span>` |
| `sections/chillpod-faq.liquid`                | Homepage (`index.json`)          | `<a class="chillpod-faq__cta button" href="/products/chillpod">Buy Now — $29.95</a>` |
| `sections/chillpod-sticky-bar.liquid`         | **Every page** (footer group `sections/footer-group.json`) | `<a class="chillpod-sticky-bar__btn" href="/products/chillpod">Buy Now</a>` plus `$29.95` and the Patent Pending line |
| `sections/chillpod-uses.liquid`, `chillpod-value.liquid`, `chillpod-proof.liquid` | Homepage | no purchase CTA observed — leave alone |

All of these CTAs currently link to `/products/chillpod` (informational — allowed by the
handoff). None link to `/cart/...` or checkout. The label is the problem, not the destination.

## Step 0 — check the theme editor first (no code)

Open **Online Store → Themes → Customize → Home page**, click each section above. If the
button label is a section setting (e.g. "Button label"), just change it to `Coming Soon`
and Save. Record the previous value ("Buy Now", "Buy Now — $29.95") so it can be restored.

For the sticky bar you can also simply hide it: in the editor, footer group →
`chillpod_sticky_bar` → eye icon (hide). Hiding is reversible and keeps its settings.

## Step 1 — if the label is hardcoded, patch the Liquid

Edit each section file and wrap the CTA. Pattern (adapt class names to what you find):

```liquid
{%- comment -%} COMING SOON PATCH {%- endcomment -%}
{%- if settings.coming_soon_mode -%}
  {%- render 'coming-soon-notice', layout: 'inline', href: '/products/chillpod' -%}
{%- else -%}
  <a class="chillpod-hero__cta button" href="/products/chillpod">Buy Now</a>
{%- endif -%}
```

If you want to keep the section's own button styling instead of Dawn's `.button`, keep the
original element and only swap the text/attributes:

```liquid
<a class="chillpod-sticky-bar__btn" href="/products/chillpod"
   {%- if settings.coming_soon_mode %} aria-label="Coming Soon - Availability coming soon"{% endif -%}>
  {%- if settings.coming_soon_mode -%}
    {{ settings.coming_soon_label | default: 'Coming Soon' | escape }}
  {%- else -%}
    Buy Now
  {%- endif -%}
</a>
```

For `chillpod-featured-cta.liquid` the whole image card is the link; keep it pointing at
`/products/chillpod` and change the inner `<span class="chillpod-featured-cta__btn">` text
and the `aria-label` with the same conditional.

For `chillpod-faq.liquid` the label includes the price ("Buy Now — $29.95"). Replace with
`Coming Soon` only — keep the price visible elsewhere (PDP and sticky bar still show $29.95;
do not change any price).

## Things to also check in these sections

- **Launch-sale countdown.** `chillpod-featured-cta` ships a 48h "launch sale" timer script
  (`window.__chillpodLaunchSaleInit`, `data-chillpod-sale-*` attributes). A countdown that
  urges purchase while ordering is off is misleading; consider hiding the timer element
  inside `{% unless settings.coming_soon_mode %}`. Optional; not a checkout path.
- **Any `/cart/67578266419311:1` or `/checkout` href.** None were observed on the live
  homepage, but search each section file (Edit code → search) for `cart/` and `checkout`
  before you finish. If any exist, swap them to `/products/chillpod` while the toggle is on.
- **Theme-editor text settings** (rich text mentioning "Buy now", "Order today") — edit in
  the editor, note the old copy in the PR/runbook so it can be restored.

## Revert

Turn off **Theme settings → Coming Soon mode**. Sections patched with the `{% if
settings.coming_soon_mode %}` conditional return to their original markup automatically.
Anything changed via editor settings (labels, hidden sticky bar) must be restored by hand
from the values you recorded in Step 0.
