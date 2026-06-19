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

## After it's live

- Replace the **Buy Now** link with your Shopify Buy Button URL.
- Fill remaining placeholders: real price, phone-fit dimensions, real reviews.
