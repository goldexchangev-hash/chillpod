# ChillPod

Landing page for **ChillPod** — a phone cooler with a frozen water core. Slide your
phone into the phone-shaped slot to keep it from overheating at the beach, on the
golf course, on the soccer sidelines, at festivals, in a hot car — anywhere it's hot.

This is a **single static `index.html`**: all CSS, JavaScript, and product images
are embedded in the one file. There is no build step.

## Local preview

Open `index.html` directly in a browser, or serve the folder:

```bash
# Python
python -m http.server 8000
# then open http://localhost:8000
```

## Deploy (Render static site)

Deployment is configured via the [`render.yaml`](render.yaml) Blueprint:

- **type:** web
- **runtime:** static
- **staticPublishPath:** `./`
- no build command — `index.html` is served as-is

To go live: in Render, **New → Blueprint**, connect this repo, pick the `main`
branch, and **Apply**. It deploys to a free `*.onrender.com` URL.

### Custom domain

Add `chillpod.com` later in Render → your site → **Settings → Custom Domains**,
then add the DNS records at your registrar. (You can also uncomment the `domains:`
block in `render.yaml`.)

## Coming Soon mode (ordering paused)

The four purchase CTAs in `index.html` (header, hero, offer card, mobile sticky bar)
currently render as non-link **Coming Soon** pills with "Availability coming soon".
This is parity for the Render page only. The live store is the Shopify Dawn theme at
ichillpod.com; stopping orders there requires the Shopify Admin + theme steps in
[`docs/COMING_SOON_DISABLE_ORDERS.md`](docs/COMING_SOON_DISABLE_ORDERS.md)
(copy-paste Dawn 16 patches in [`theme-patches/dawn/`](theme-patches/dawn/README.md)).

## After it's live (normal mode)

- All purchase CTAs link to the Shopify cart permalink
  `https://ichillpod.myshopify.com/cart/67578266419311:1` (adds one iChillPod,
  variant `67578266419311` of product `15554226356335`, and goes straight to
  checkout). To leave Coming Soon mode, restore those four `<a>` tags in
  `index.html` (the exact markup is in the HTML comment at the bottom of the file).
  If the variant ever changes, update that URL in the same four places.
- Fill remaining placeholders: real price, phone-fit dimensions, real reviews.
