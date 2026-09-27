# iChillPod — Shopify SEO: paste-ready implementation

**Date:** 2026-09-27 · **Live site:** https://ichillpod.com (public Shopify store, password removed) · **Scope:** on-page SEO for the three indexable URLs. **This repo does not contain the Shopify theme** — nothing in this PR changes the live store. Every change below is applied by hand in Shopify Admin or the theme code editor; this document is the exact copy to paste.

> **CRITICAL CLAIM CHANGE — read first.** The canonical bare-phone shutdown time is now **5 minutes** (as shown in the homepage proof H2 "5 Minutes Bare. 30 Minutes+ in iChillPod."). It is **not** 8 minutes. Several live spots still say 8 minutes (list in §1.4). Every string in this doc uses **5 minutes bare / 30 minutes+ in iChillPod**. Do not paste any 8-minute copy anywhere.

Legend: **P0** = do before anything else (indexing / claims / broken data) · **P1** = this week · **P2** = follow-up.

---

## 0. Where things live in Shopify Admin (click map)

| What | Where to click |
|---|---|
| Homepage title + meta description | **Online Store → Preferences → Title and meta description** (fields "Homepage title", "Homepage meta description") |
| Product title tag / meta / URL handle | **Products → iChillPod (`chillpod`) → scroll to "Search engine listing" → Edit** |
| Product description body (fixes visible 8-min copy *and* the Product JSON-LD description Dawn generates) | **Products → iChillPod → Description** (rich-text editor) |
| Product `brand.name` in JSON-LD | **Products → iChillPod → Product organization → Vendor** = `iChillPod` |
| Product image alt text | **Products → iChillPod → Media → click an image → "Add alt text"** (or **Content → Files → image → Alt text**) |
| Homepage section images (Beach/Sauna/Stadium/Golf tiles) alt text | **Content → Files → image → Alt text** (Dawn reads the file's alt), or the section's image-alt setting in **Online Store → Themes → Customize** if the section exposes one |
| Our Story title tag / meta | **Online Store → Pages → Our Story → Search engine listing → Edit** |
| Theme code (JSON-LD blocks, og:image https, Organization url, header H1) | **Online Store → Themes → … (three dots) → Edit code** (duplicate the theme first: **… → Duplicate**, edit the copy, preview, then publish) |
| Homepage FAQPage JSON-LD (no code editor needed) | **Online Store → Themes → Customize → Home page → Add section → "Custom Liquid"** → paste block → set the section to have no padding |
| Social links (fills `sameAs`) | **Online Store → Themes → Customize → Theme settings → Social media** |
| Delete leftover example collection | **Products → Collections → "asset-pack-14024179714-example-products" → Delete** |

---

## 1. Audit — what the live pages serve today (verified 2026-09-27)

Fetched with `curl` and parsed; numbers are from the live HTML, not the crawl notes.

### 1.1 Homepage `https://ichillpod.com/`

| Element | Live value | Verdict |
|---|---|---|
| `<title>` | `iChillPod.com` | Brand-only; no keyword, no benefit. **P0** |
| Meta description | *(none)* | Google writes its own snippet. **P0** |
| Canonical | `https://ichillpod.com/` | OK |
| H1s | **Two**: Dawn wraps the header logo in an `<h1>` on the homepage (image-only, reads as empty), plus the hero `Your Phone Dies in the Heat. iChillPod Won't Let It.` | Make the hero the only H1. **P1** |
| H2s | `Item added to your cart` (hidden cart drawer), `From the Beach to the Sidelines.`, `A Pouch Delays the Heat. iChillPod Pulls It Out.`, `5 Minutes Bare. 30 Minutes+ in iChillPod.`, `FAQ`, `Quick links`, `Subscribe to our emails` | No H2 contains "sauna" even though the proof section is a sauna test. **P1** |
| Proof copy | H2 and card say **5:00**; the disclaimer pill below still says **"8 vs 30 minutes+" is from our own testing** | Contradiction on the same screen. **P0** |
| Image alts | Tiles: `Beach`, `Sauna`, `Stadium`, `Golf`; proof photo `Woman in a sauna holding iChillPod`; CTA `iChillPod in a cooler` | Tiles are one-word; the rest is fine. **P1** |
| JSON-LD | `Organization` (9 empty strings in `sameAs`) + `WebSite` (SearchAction). No `Product`, no `FAQPage` despite a 9-question FAQ | **P1** |
| Open Graph | `og:title` = `iChillPod.com`, `og:description` = `iChillPod`, **no `og:image`**, `og:type` = website; Twitter card mirrors it | Shares render as a bare grey card. **P0** (fixed automatically by the title/meta + a social image) |
| Hero video | Single `<source>` → `…HD-1080p-4.8Mbps-95647115.mp4`, **8,575,586 bytes**, `autoplay muted loop`, `preload="metadata"`, poster `hero-poster.jpg` (72 KB) | Biggest LCP/bandwidth cost on the site; 1080p for a ~500 px square slot. **P1** |
| Price on page | `$29.95` (was `$39`), 48-h evergreen countdown, "Patent Pending — U.S. App. No. 64/086,049" | Matches product JSON-LD offer |

### 1.2 Product `https://ichillpod.com/products/chillpod`

| Element | Live value | Verdict |
|---|---|---|
| `<title>` / H1 | `iChillPod - No-Power Phone Cooler for Saunas` | Good — keep |
| Meta description | Raw dump of the product body (`Your Phone Dies in the Heat… A Pouch Delays the Heat… gives your`) truncated mid-sentence; same text in `og:description` / `twitter:description` | No SEO meta set, so Dawn falls back to the body. **P0** |
| Body copy | H3 `8 Minutes Bare. 30 Minutes in iChillPod.`, `Bare phone: thermal shutdown at 8:00`, `"8 vs 30 minutes" is from our own testing` | **8-minute claim — must become 5. P0** |
| Product JSON-LD | `Product` with `brand.name: "ChillPod"`, `name` = full title, `description` = body dump (8-min claim), `sku CHILLPOD-001`, offer `29.95 USD InStock`, one image | Brand name wrong; description carries the 8-min claim. **P0** |
| `og:image` | `http://ichillpod.com/cdn/shop/files/sauna-bench-featured-fill-1376.jpg` (**http**), `og:image:secure_url` is https | Dawn default; LinkedIn/Slack sometimes refuse the http one. **P1** |
| Image alts | `iChillPod phone cooler on sauna bench`, `iChillPod phone cooler packed in ice inside a cooler`, `sauna branded`, then **four empty alts** on `use-beach.jpg`, `use-sauna.jpg`, `use-stadium.jpg`, `use-golf.jpg` (thumbnails fall back to the product title) | **P1** |
| Canonical / sitemap | Canonical self-referencing; listed in `sitemap_products_1.xml` with image title/caption | OK |

### 1.3 Our Story `https://ichillpod.com/pages/our-story`

| Element | Live value | Verdict |
|---|---|---|
| `<title>` / H1 | `How iChillPod Was Made.` | Weak; no topic word. **P2** |
| Meta description | `How ChillPod was made — from a home sauna that runs hot to a phone cooler you can take to the beach.` (100 chars, brand spelled "ChillPod") | Short; fix brand spelling. **P2** |
| Body | Says "After about **five minutes** of using my phone in there … it would overheat and shut down." | Already consistent with the 5-minute claim |
| Organization JSON-LD | `"url": "https://ichillpod.com/pages/our-story"` | Dawn's `request.origin \| append: page.url` bug — Organization URL must be the site root on every page. **P1** |

### 1.4 Every live spot that still says 8 minutes (fix all — P0)

1. Homepage → proof section disclaimer pill: `"8 vs 30 minutes+" is from our own testing — not a third-party stat.` → `"5 vs 30 minutes+" is from our own testing — not a third-party stat.`
2. Product page body H3: `8 Minutes Bare. 30 Minutes in iChillPod.` → `5 Minutes Bare. 30 Minutes+ in iChillPod.`
3. Product page body: `Bare phone: thermal shutdown at 8:00. In iChillPod: still going at 30:00.` → `Bare phone: thermal shutdown at 5:00. In iChillPod: still going at 30:00.`
4. Product page body: `"8 vs 30 minutes" is from our own testing — not a third-party stat.` → `"5 vs 30 minutes+" is from our own testing — not a third-party stat.`
5. Product JSON-LD `description` (auto-generated from the body — fixed by 2–4, or replaced by the block in §4.1).
6. Meta / `og:description` fallbacks on the product page (replaced by §2.2).
7. Render legacy `index.html` in this repo (fixed in this PR).

### 1.5 Site-level

- `robots.txt`: standard Shopify; `Allow: /`. OK.
- `/sitemap.xml` index → products (home + `/products/chillpod`), pages (`/pages/contact`, `/pages/data-sharing-opt-out`, `/pages/our-story`), collections (`/collections/frontpage`, **`/collections/asset-pack-14024179714-example-products`** ← leftover demo collection, delete it), blogs (`/blogs/news`, empty).
- **Google Search Console: the `ichillpod.com` property is not in the connected account** (only `yachtbazar` is). Nobody can submit the sitemap or see impressions until the merchant adds and verifies it (§7).

---

## 2. Titles & meta descriptions — paste exactly

### 2.1 Homepage — `Online Store → Preferences → Title and meta description`

**Homepage title** (61 chars):

```
iChillPod — Sauna Phone Cooler That Pulls Heat Out (No Power)
```

**Homepage meta description** (160 chars):

```
No-power sauna phone cooler that pulls heat out — not just a pouch. Freeze it, keep filming. Tested so your phone lasts through the heat. $29.95, free shipping.
```

Dawn only appends ` – iChillPod` to the title when the title does not already contain the shop name, so the title above renders exactly as written.

**Why this title and not `iChillPod — Cool Your Phone, Keep It From Overheating`?**

- The benefit-first version contains no phrase anyone types. "Cool your phone" and "keep it from overheating" are outcomes, not queries; Google matches titles against query terms, and a new domain with ~zero links needs that exact-match help more than an established brand does.
- The commercial queries in this niche are "sauna phone case" (top autocomplete for "sauna phone"), "sauna phone cooler", "sauna phone pouch/bag", "sauna proof phone case" (see `docs/seo-keyword-research.md` on the research branch; all volumes unverified). Boundless titles itself "Sauna Safe Phone Case™", TempSafe and SaunaPal also win on "sauna phone case". Nobody titles on "sauna phone cooler" — it is the open head term, and "cooler" is the honest category for a product that actively removes heat rather than insulating.
- "Pulls Heat Out" is the differentiator against every insulation-only competitor and doubles as the description of what a cooler does. "(No Power)" captures the empty "phone cooler no battery / without electricity" long tail and disqualifies the gaming-fan intent that owns generic "phone cooler".
- Benefit-first copy still gets its place: it is the H1 (`Your Phone Dies in the Heat. iChillPod Won't Let It.`), which is what visitors read, while the title is what Google reads.

### 2.2 Product `/products/chillpod` — `Products → iChillPod → Search engine listing → Edit`

**Page title** (keep, 44 chars):

```
iChillPod - No-Power Phone Cooler for Saunas
```

**Meta description** (154 chars):

```
No-power sauna phone cooler — pulls heat out, not just a pouch. Freeze it, keep filming ~30+ min. Patent pending. $29.95, free shipping, 30-day guarantee.
```

**URL handle:** keep `chillpod` (it is already indexed; changing it would only cost a redirect).

### 2.3 Our Story `/pages/our-story` — `Online Store → Pages → Our Story → Search engine listing → Edit`

**Page title** (48 chars):

```
How iChillPod Was Made — From a 200°F Home Sauna
```

**Meta description** (154 chars):

```
How iChillPod was made: a 200°F home sauna kept shutting down my phone, so I designed a sauna phone cooler with a frozen core — then took it to the beach.
```

Also fix the on-page spelling "ChillPod" → "iChillPod" in the page body where it appears.

---

## 3. Product page body — replace the proof paragraph (fixes visible copy, meta fallback and JSON-LD description at once)

`Products → iChillPod → Description`. Replace the proof block (the H3 and the two lines under it) with:

```
5 Minutes Bare. 30 Minutes+ in iChillPod.
We put it in a 200°F sauna — about twice the temperature your phone is rated for. Bare phone: thermal shutdown at 5:00. In iChillPod: still going at 30:00. If it survives 200°F, a hot beach bag doesn't stand a chance.
"5 vs 30 minutes+" is from our own testing — not a third-party stat.
```

Leave the rest of the body (pouch comparison, free shipping · 30-day · Patent Pending — U.S. App. No. 64/086,049) as is.

Set **Product organization → Vendor** to `iChillPod` (Dawn's `{{ product | structured_data }}` uses the vendor as `brand.name`; today it is `ChillPod`).

---

## 4. JSON-LD

### 4.1 Product JSON-LD (product page) — theme code, optional but recommended

Dawn already emits Product JSON-LD via `{{ product | structured_data }}` in `sections/main-product.liquid` (search the file for `application/ld+json`). After §3 that block will have the right brand, price and a 5-minute description, but its `name` will remain the full title. If you want `name: "iChillPod"` plus return/shipping details (Merchant listing eligibility), replace that `<script type="application/ld+json">…</script>` with:

```liquid
{%- assign v = product.selected_or_first_available_variant -%}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "@id": "{{ shop.url }}{{ product.url }}#product",
  "name": "iChillPod",
  "alternateName": {{ product.title | json }},
  "url": "{{ shop.url }}{{ product.url }}",
  "brand": { "@type": "Brand", "name": "iChillPod" },
  "sku": {{ v.sku | json }},
  "category": "Phone Cooler",
  "image": [
    {%- for image in product.images -%}
      {{ image | image_url: width: 1920 | prepend: 'https:' | json }}{%- unless forloop.last -%},{%- endunless -%}
    {%- endfor -%}
  ],
  "description": "iChillPod is a no-power sauna phone cooler. A frozen water core sits against your phone and pulls heat out by direct conduction — it is not an insulated pouch. Freeze it, slide your phone in, and keep filming in the sauna, at the beach, or anywhere hot. In our 200°F sauna test a bare phone shut down in about 5 minutes; in iChillPod it was still recording at 30 minutes+. Fits iPhone and Android phones up to the iPhone 18 Pro Max size ceiling (163.4 × 78.0 × 8.75 mm). Refreezes overnight and reuses. Free shipping, 30-day money-back guarantee. Patent Pending — U.S. App. No. 64/086,049.",
  "offers": {
    "@type": "Offer",
    "@id": "{{ shop.url }}{{ v.url }}#offer",
    "url": "{{ shop.url }}{{ v.url }}",
    "price": "{{ v.price | divided_by: 100.0 }}",
    "priceCurrency": {{ cart.currency.iso_code | json }},
    "itemCondition": "https://schema.org/NewCondition",
    "availability": "{% if v.available %}https://schema.org/InStock{% else %}https://schema.org/OutOfStock{% endif %}",
    "seller": { "@type": "Organization", "name": "iChillPod", "url": {{ shop.url | json }} },
    "hasMerchantReturnPolicy": {
      "@type": "MerchantReturnPolicy",
      "applicableCountry": "US",
      "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
      "merchantReturnDays": 30,
      "returnMethod": "https://schema.org/ReturnByMail",
      "returnFees": "https://schema.org/FreeReturn"
    },
    "shippingDetails": {
      "@type": "OfferShippingDetails",
      "shippingRate": { "@type": "MonetaryAmount", "value": "0", "currency": "USD" },
      "shippingDestination": { "@type": "DefinedRegion", "addressCountry": "US" }
    }
  }
}
</script>
```

Today this renders `price: 29.95`, `priceCurrency: USD`, `availability: InStock`, `sku: CHILLPOD-001`. **Confirm before pasting:** `applicableCountry` / `shippingDestination` are set to `US` and `returnFees` to `FreeReturn` because the page promises "free shipping · 30-day money-back guarantee"; if you ship or accept returns from other countries, or charge return postage, edit those values (or delete the two sub-objects) — do not publish policy you do not honour.

### 4.2 FAQPage JSON-LD (homepage) — no code editor needed

`Online Store → Themes → Customize → Home page → Add section → Custom Liquid`, paste the block below, save. (Custom Liquid renders inside `<body>`, which is valid for JSON-LD.) Answers mirror the live FAQ accordion; timing uses **5 minutes bare**. Two edits versus the visible FAQ that you should also make in the accordion itself: "Each **ChillPod** is 3D printed" → "Each **iChillPod**…", and the "Water/sand resistance: IP rating TBC" fragment is omitted here (remove it from the visible Specs answer or fill it in).

Note: since Aug 2023 Google shows FAQ rich results only for government/health sites, so expect no dropdowns in the SERP. The value is entity clarity (Google/Bing/LLM answer engines read the Q&A directly) and it costs nothing.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "@id": "https://ichillpod.com/#faq",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Does It Actually Work, or Is It Just a Pouch?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "It actively removes heat — a pouch only insulates. The frozen core sits against your phone so heat flows out into the core. In our 200°F sauna test: about 5 minutes bare vs 30 minutes+ in iChillPod."
      }
    },
    {
      "@type": "Question",
      "name": "How Does It Work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Take the green cap off, fill the bottle with water, and let it freeze. Once frozen, snap the cap back on and slip your phone into the cooler. Important: do not fill over 90% of the volume. Water expands as it freezes and can crack or break the bottle — never fill it to the brim."
      }
    },
    {
      "@type": "Question",
      "name": "What Phones Fit?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Fits the iPhone 18 Pro Max (163.4 × 78.0 × 8.75 mm) and everything smaller. That's the size ceiling — anything larger may not fit. Popular fits include iPhone 18 / 17 / 16 (including Pro Max), Samsung Galaxy S26, S26+ and S26 Ultra, Google Pixel 10, Pixel 10 Pro and Pixel 10 Pro XL, OnePlus 13, Xiaomi 15 Ultra, and more flagships at or under that size."
      }
    },
    {
      "@type": "Question",
      "name": "Will It Work With My Phone Case?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We've tested it — some phone cases work, and some don't. Cases that are too wide or too thick may not slide into the slot. There are thousands of case styles out there, so we can't guarantee a fit with the case on. We recommend taking your phone out of its case and using it that way — especially in the sauna."
      }
    },
    {
      "@type": "Question",
      "name": "How Long Does One Freeze Last?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Long enough for a beach trip, a round of golf, or a full game. Up to seven hours in a gym bag. Refreezes overnight and reuses all summer."
      }
    },
    {
      "@type": "Question",
      "name": "Will It Get My Phone Wet?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Condensation can form on the cooler as the frozen core warms. Wipe it off before you pocket the phone."
      }
    },
    {
      "@type": "Question",
      "name": "Specs & Fit",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Fits phones up to the iPhone 18 Pro Max size ceiling (163.4 × 78.0 × 8.75 mm). Supports modern iPhone, Samsung Galaxy, and Google Pixel flagships within that envelope. Runtime per freeze: up to seven hours. No power, cables or batteries — refreeze and reuse."
      }
    },
    {
      "@type": "Question",
      "name": "Shipping & Returns",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Free shipping. 30-day money-back guarantee — try it through one hot weekend."
      }
    },
    {
      "@type": "Question",
      "name": "How Long Does Shipping Take?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Each iChillPod is 3D printed, so ship times depend on print time and whether we're in backorder. If it's on backorder, it can take a little longer than the usual day or two. That said, we've been getting orders out virtually the same day."
      }
    }
  ]
}
</script>
```

### 4.3 Organization JSON-LD — fix `url` and empty `sameAs` (theme code: `sections/header.liquid`)

Dawn's header emits the Organization block with `"url": {{ request.origin | append: page.url | json }}` — on `/pages/our-story` that becomes the story URL — and prints all nine social settings even when blank (hence nine `""`). Find the `<script type="application/ld+json">` block in `sections/header.liquid` and replace it with:

```liquid
{%- capture social_links -%}
  {{ settings.social_twitter_link }}|{{ settings.social_facebook_link }}|{{ settings.social_pinterest_link }}|{{ settings.social_instagram_link }}|{{ settings.social_tiktok_link }}|{{ settings.social_tumblr_link }}|{{ settings.social_snapchat_link }}|{{ settings.social_youtube_link }}|{{ settings.social_vimeo_link }}
{%- endcapture -%}
{%- assign social_links = social_links | strip | split: '|' -%}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "{{ shop.url }}/#organization",
  "name": {{ shop.name | json }},
  "url": {{ shop.url | json }},
  {%- if section.settings.logo -%}
  "logo": {
    "@type": "ImageObject",
    "url": {{ section.settings.logo | image_url: width: 500 | prepend: "https:" | json }},
    "width": 500,
    "height": {{ 500 | divided_by: section.settings.logo.aspect_ratio | round }}
  },
  {%- endif -%}
  "description": "Maker of iChillPod, the no-power sauna phone cooler with a frozen core that pulls heat out of your phone.",
  "sameAs": [
    {%- assign first = true -%}
    {%- for link in social_links -%}
      {%- assign l = link | strip -%}
      {%- if l != blank -%}
        {%- unless first -%},{%- endunless -%}{{ l | json }}
        {%- assign first = false -%}
      {%- endif -%}
    {%- endfor -%}
  ]
}
</script>
```

`shop.url` renders `https://ichillpod.com` on every page. Then fill the real profiles under **Customize → Theme settings → Social media** so `sameAs` is non-empty (Instagram/TikTok/YouTube are the ones that matter for a demo-video product).

### 4.4 Keep as is

`WebSite` + `SearchAction` on the homepage is fine. Do not add Product JSON-LD to the homepage (it would create two Product entities for one product; the PDP is the canonical product entity).

---

## 5. Open Graph / social

- **Homepage `og:image`:** none today. Set **Customize → Theme settings → Social media → Social sharing image** to a 1200×630 export of the sauna-bench product photo (`sauna-bench-featured-fill-1376.jpg`, currently 1376×768, works but is 16:9 — export a 1.91:1 crop for Facebook/LinkedIn). Dawn then emits `og:image` on every page that has no page image of its own.
- **Product `og:image` uses `http:`:** Dawn's `snippets/meta-tags.liquid` hardcodes it. In that file change

  ```liquid
  <meta property="og:image" content="http:{{ page_image | image_url: width: 1200 }}">
  ```
  to
  ```liquid
  <meta property="og:image" content="https:{{ page_image | image_url: width: 1200 }}">
  ```
  (leave the `og:image:secure_url` line as it is).
- `og:title` / `og:description` / `twitter:*` inherit from the title and meta above — nothing extra to set.
- After publishing, re-scrape once at https://developers.facebook.com/tools/debug/ and https://www.linkedin.com/post-inspector/ so cached grey cards are refreshed.

---

## 6. Images, headings, video

### 6.1 Product image alt text — `Products → iChillPod → Media → image → Add alt text`

| File | Alt text to paste |
|---|---|
| `use-beach.jpg` | `iChillPod phone cooler keeping a phone cool at the beach` |
| `use-sauna.jpg` | `iChillPod phone cooler in a sauna to prevent overheating` |
| `use-stadium.jpg` | `iChillPod phone cooler used at a hot outdoor stadium` |
| `use-golf.jpg` | `iChillPod phone cooler for a phone on a hot golf course` |
| `sauna-branded.png` (currently `sauna branded`) | `iChillPod sauna phone cooler with the ChillPod logo on a sauna bench` |

The same four files are used as the homepage "Uses" tiles (alts `Beach` / `Sauna` / `Stadium` / `Golf`). Set the alt once in **Content → Files** and both placements pick it up.

### 6.2 Headings (theme editor copy fields — no code)

- **Header logo H1 (P1):** in `sections/header.liquid`, Dawn wraps the logo in `<h1 class="header__heading">` when `request.page_type == 'index'`. Change that `<h1 …>`/`</h1>` pair to `<div class="header__heading h1">`/`</div>` so the hero heading is the page's only H1. (Keep the `h1` class for identical styling.)
- **Uses H2:** `From the Beach to the Sidelines.` → `From the Sauna to the Sidelines.` (the section already has a Sauna tile; this puts the money term in an H2 without stuffing).
- **Proof eyebrow/H2:** keep `5 Minutes Bare. 30 Minutes+ in iChillPod.`; change the eyebrow above it from `THE PROOF` → `THE 200°F SAUNA TEST`.
- **Pouch H2:** keep. In the paragraph under it, change "A pouch is a blanket" → "An insulated pouch or sauna phone case is a blanket" to pick up the competitor phrasing naturally.
- **FAQ H2:** `FAQ` → `iChillPod FAQ` (tiny, but "FAQ" alone is a wasted heading).

### 6.3 Hero video (P1)

Live: one MP4 source, 1080p @ 4.8 Mbps, **8.6 MB** for a ~14 s loop that displays in a ≤ 500 px square. Options, best first:

1. **Re-upload a pre-compressed rendition** (Content → Files, or replace the video in the hero section). Target ≤ 1.5 MB: 720×720 (or 720p), H.264, CRF 28–30, no audio track, fast-start. From the square master in this repo:

   ```bash
   ffmpeg -i hero-demo.mp4 -an -vf "scale=720:-2" -c:v libx264 -preset slow -crf 29 \
     -pix_fmt yuv420p -movflags +faststart hero-demo-720.mp4
   ```
   Shopify will still transcode, but its ladder starts from the file you upload, so a smaller master yields smaller renditions.

2. **Let Shopify serve its own ladder** instead of a single hardcoded 1080p source. In the hero section Liquid, replace the hand-written `<video><source …HD-1080p…></video>` with the `video_tag` filter, which emits 1080p/720p/480p MP4 sources plus HLS and lets the browser choose:

   ```liquid
   {{ section.settings.hero_video
      | video_tag:
          image_size: '1100x',
          autoplay: true,
          loop: true,
          muted: true,
          controls: false,
          preload: 'metadata',
          playsinline: true,
          class: 'chillpod-hero__video',
          poster: section.settings.hero_poster | image_url: width: 1100 }}
   ```

3. **Minimum-change HTML** if you keep a hand-written tag (this is what the markup should look like; `poster` should be an explicit, small JPEG so LCP paints before the video):

   ```liquid
   {%- assign poster_url = section.settings.hero_poster | image_url: width: 1100 | prepend: 'https:' -%}
   <video class="chillpod-hero__video"
          poster="{{ poster_url }}"
          preload="metadata"
          autoplay muted loop playsinline
          width="1100" height="1100"
          aria-label="iChillPod demo: an overheating phone is set into the cooler in a sauna and comes back on">
     <source src="{{ section.settings.hero_video.sources | where: 'height', 720 | map: 'url' | first }}" type="video/mp4">
   </video>
   ```
   Also add `<link rel="preload" as="image" href="{{ poster_url }}" fetchpriority="high">` in `layout/theme.liquid` for the homepage only (`{% if request.page_type == 'index' %}`).

Do **not** delete the video — it is the proof; just make it cheaper.

---

## 7. Google Search Console (P0 — nothing else can be measured until this is done)

The connected GSC account only contains `yachtbazar`; there is **no property for ichillpod.com**, so the coordinator could not submit the sitemap or inspect URLs. The merchant (or whoever owns the domain DNS / Shopify admin) must:

1. Go to https://search.google.com/search-console → property selector → **Add property**.
2. Choose **URL prefix** and enter exactly `https://ichillpod.com/` (URL-prefix is enough for a single-host store; use Domain property only if you can add a DNS TXT record and want `www`/`http` variants covered too).
3. Verify with one of:
   - **HTML tag:** copy the `<meta name="google-site-verification" content="…">` tag → Shopify **Online Store → Themes → Edit code → `layout/theme.liquid`** → paste inside `<head>` (before `{{ content_for_header }}`) → Save → click **Verify**.
   - **DNS TXT record:** add the `google-site-verification=…` TXT record at the registrar for `ichillpod.com` → Verify (can take up to an hour to propagate).
4. In the new property: **Sitemaps → Add a new sitemap →** enter `sitemap.xml` (resolves to `https://ichillpod.com/sitemap.xml`) → Submit. Shopify keeps it current automatically.
5. **URL Inspection** → paste `https://ichillpod.com/` → **Request indexing**; repeat for `/products/chillpod` and `/pages/our-story`.
6. Add the same property to **Bing Webmaster Tools** (import from GSC in one click) — Bing/Copilot/DuckDuckGo traffic is free.
7. After a week: check **Pages → Not indexed** for the `asset-pack-…-example-products` collection (delete the collection in Admin so it drops out of the sitemap) and **Enhancements → Merchant listings** for the Product schema.

Add the coordinator's Google account as a **Full** user under Settings → Users and permissions if you want them to monitor it.

---

## 8. Prioritised action list

**P0 — today**
1. Fix the 5-vs-8 minute contradictions everywhere (§1.4, §3). A proof claim that disagrees with itself on the same page costs more trust than any SEO gain.
2. Homepage title + meta (§2.1). Product meta (§2.2). Vendor = `iChillPod` (§3).
3. Add + verify GSC property, submit sitemap (§7).
4. Set a social sharing image in theme settings (§5) so shares stop rendering blank.

**P1 — this week**
5. Product image alts (§6.1). FAQPage Custom Liquid section on the homepage (§4.2).
6. Organization block fix in `header.liquid` (§4.3) + fill social links. `og:image` https in `meta-tags.liquid` (§5). Header logo H1 → div (§6.2).
7. Hero video: upload a ≤ 1.5 MB 720 px rendition and switch to `preload="metadata"` + explicit poster (§6.3).
8. Delete the example-products collection.
9. Heading tweaks in the theme editor (§6.2) — "From the Sauna to the Sidelines.", "THE 200°F SAUNA TEST".

**P2 — next**
10. Our Story title/meta (§2.3) and body brand spelling.
11. Content hub on `/blogs/news` (already in the sitemap, empty): "Can you bring your phone into a sauna?", "How to keep your phone from overheating in a sauna", "HOTWORX phone overheating — what actually works", "Best sauna phone case vs cooler (2026)". These are the informational clusters (C, B, D in the research doc) where every ranking page currently says "just don't" — the 5-vs-30 test is the answer they lack. One post per month is enough at this volume.
12. Optional Product JSON-LD override for `name: "iChillPod"` + return/shipping details (§4.1) once return/shipping countries are confirmed.
13. Reviews: once real orders exist, install a reviews app that emits `aggregateRating` on the PDP; do not hand-write ratings into schema.
14. Render legacy site: `chillpod-6d7v.onrender.com` still serves an older copy of the same page (price shows $29, proof updated to 5 min in this PR). It now carries `rel="canonical"` → `https://ichillpod.com/` so it cannot compete with the store; treat it as a staging/preview only, or suspend the Render service when it is no longer needed.

---

## 9. What this PR does and does not do

- **Does:** adds this document; updates the legacy Render `index.html` in this repo to the same title/meta, the 5-minute claim, a canonical to `https://ichillpod.com/`, OG/Twitter tags, Organization + Product + FAQPage JSON-LD, `preload="metadata"` on the demo video, and descriptive alts on the four use-case tiles.
- **Known mismatch on the Render copy (not fixed here — pricing is out of scope):** the Render page still displays `$29` while the store charges `$29.95`. The new meta description uses the store price (`$29.95`, per the approved string); the Render Product JSON-LD offer is `29.00` because structured data must match the visible page price. Either update the Render price display to `$29.95` or retire the Render site; with the canonical in place Google will index the store, not this copy.
- **Does not:** touch the live Shopify store, pricing, checkout, or Render deploy settings. No Shopify theme files are in this repository; every Shopify change above is manual.
