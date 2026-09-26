# iChillPod — Launch Readiness Audit

**Audited commit:** `0b9b47a` (`main`, "Update sauna temperature claim from 180°F to 200°F (#4)")
**Live site checked:** https://ichillpod.com (served from Render static site `chillpod-6d7v.onrender.com` behind Cloudflare; live HTML `ETag` matches `origin/main` byte-for-byte)
**Audit date:** 2026-09-26
**Scope:** read-only audit. No product code was changed. No redesign was implemented. Nothing was merged.

The site is a single static file (`index.html`, 468 lines, 101.7 KB) plus media, deployed via `render.yaml`. All line references below are to `index.html` at the audited commit unless stated otherwise.

**How findings were verified:** static review of `index.html` / `render.yaml` / `README.md`; headless Chromium (Playwright) renders at 360 / 375 / 390 / 820 / 1280 px with mobile emulation; `ffprobe` on the videos; JPEG header parsing for image dimensions; `curl` against the live domains and assets; WCAG contrast math on the CSS palette; DNS/whois-style checks on `chillpod.com` vs `ichillpod.com`.

---

## Executive summary — what blocks launch today

1. **You cannot buy the product.** The Shopify Buy Button is fully scaffolded but every credential is a `TODO` placeholder (`index.html:445-447`), so the guard at `:449` bails out and the button never mounts. The only "purchase" path on the live site is `mailto:hello@chillpod.com` (`:324`).
2. **That fallback email goes to a domain you do not own.** `chillpod.com` resolves to a third-party AWS S3 bucket (`3.230.199.117` / `35.168.67.138`, HTTP 403 "AccessDenied"), not to your Render service. Pre-order emails from the live site are being sent to a stranger's domain (or bounce). The real inbox is `ichillpod@gmail.com` (per draft PR #2).
3. **The page overflows horizontally on every phone.** At 360/375/390 px the document is 459 px wide. The sauna photo and the "8 vs 30 minutes" proof cards are clipped off the right edge and the sticky "Buy now" bar is cut to "Bu…". Root cause is one CSS rule (`:100-101`); a one-line fix is verified below.
4. **Visible placeholder copy in the FAQ.** Ten `[TBC]` / `[X hours]` / `[Insert runtime…]` yellow-dashed placeholders are live (`:346-370`), including in the "Specs & Fit" and "Shipping & Returns" answers.
5. **Fake urgency.** "Launch sale ends in 59:53" is an evergreen 1-hour timer that silently resets from `localStorage` (`:465`). Combined with a never-charged strikethrough "was $39", this is an FTC / consumer-protection exposure and a trust killer if anyone notices.

Three sibling **draft** PRs already exist and overlap with several fixes here. They were not merged or modified by this audit; see "Relationship to existing draft PRs" at the end.

---

## A) Prioritized findings

### Critical (blocks launch or damages trust/legal standing)

| # | Finding | Where | Evidence / notes |
|---|---|---|---|
| C1 | Shopify credentials are placeholders; checkout is impossible | `index.html:445-447`, guard `:449` | `SHOP_DOMAIN='TODO-YOUR-SHOP.myshopify.com'`, `STOREFRONT_TOKEN='TODO-…'`, `PRODUCT_ID='TODO-…'`. See Section C for the exact steps. |
| C2 | Fallback CTA emails a domain the owner does not control | `index.html:324` (`mailto:hello@chillpod.com`) | `chillpod.com` → AWS S3 bucket (403). `README.md:34` and the commented `render.yaml:8-9` also reference `chillpod.com`. Change to `ichillpod@gmail.com` (draft PR #2 does this). |
| C3 | Horizontal overflow on all phone widths (459 px document on 360–390 px viewports) | `index.html:100` `.demo{grid-template-columns:1fr 1fr}` + `:101` `.demo .card{aspect-ratio:5/6}` | `1fr` = `minmax(auto,1fr)`; the `aspect-ratio` transfers the card's content min-height into a ~213 px min-width, so 2 × 213 + 14 gap = 439 px inside a 335 px container. **Verified fixes** (each brings `scrollWidth` back to 375): `grid-template-columns:minmax(0,1fr) minmax(0,1fr)`, or `.demo .card{min-width:0}`, or stack to one column ≤ 640 px. Side-effects today: `.proof-grid`, `figure.proof-photo`, `h2`, `.stickybar` all stretch to 459 px; sticky CTA text truncated. |
| C4 | Placeholder text visible to customers | `index.html:346, 350, 359-362, 368, 370` | `[confirm fit / case range at launch]`, `[Insert runtime — e.g. "X hours per freeze."]`, `[overnight]`, `[size range TBC]`, `[TBC]`, `[X hours]`, `[IP rating TBC]`, `[X business days]`, `[policy TBC]`. Styled with `.ph` (`:36`) so they are highlighted, not hidden. |
| C5 | Fake countdown timer and unsubstantiated reference price | `:211`, `:311` (markup), `:465` (logic), `:210`/`:315`/`:319` (`$39`, `$78` strikethroughs) | Timer is `now + 1h`, re-armed on expiry. Git history shows `$39` was set on `7bb3163` and cut to `$29` on `bbdc0bb` with no sales in between — the "former price" was never a real selling price. Recommendation: remove the timer (or bind it to a real, fixed end date and remove it afterwards) and either drop the strikethrough or run the product at $39 genuinely first. |
| C6 | No refund / privacy / terms / shipping policy anywhere on the site | footer `:378-382` | The site promises "30-day money-back guarantee" and "Free shipping" (`:210`, `:213`, `:325-329`, `:369`) with no policy text. Shopify checkout will link to Shopify-hosted policies once created, but Meta/Google Ads and basic trust require links on the landing domain too. |

### Important (should be fixed before paid traffic)

| # | Finding | Where | Evidence / notes |
|---|---|---|---|
| I1 | Price and CTA are below the fold on mobile | `:175` `.hero-figure{order:-1}` (≤ 820 px) | Measured buy-box top: 787 px (360×800), 774 px (375×667), 753 px (390×844); H1 top 491–521 px. On an iPhone SE the first viewport is video + caption only. The 255–270 px square video also leaves large dead margins. Recommend headline → price/CTA → video on phones (PR #3 does "headline first"). |
| I2 | Hero video is 7.26 MB and over-specified | `hero-demo.mp4`, `<video … preload="auto">` `:223`, CSS `:78` | `ffprobe`: 1424×1424, H.264, 4.13 Mbps, 14.0 s, **includes an AAC audio track** although always muted. Rendered at ≤ 480 CSS px. Re-encode to 960×960 (or 720×720 mobile source), CRF ~28, `-an`, `-movflags +faststart`; add a VP9/AV1 WebM `<source>`. Expected 1.5–2.5 MB. `preload="auto"` forces the full download on cellular. |
| I3 | Media is never browser-cached | live headers on `hero-demo.mp4`: `cache-control: public, max-age=0, s-maxage=300` | Every visit revalidates 7 MB+ of assets. Assets are already cache-busted (`?v=2`), so add long-lived `Cache-Control` headers via a `headers:` block in `render.yaml` (`path: /*.mp4`, `/*.jpg` → `public, max-age=31536000, immutable`). |
| I4 | 68 KB base64 JPEG inlined in the HTML | `:310` | An 864×1152 JPEG (50 KB raw, 68,824 base64 chars = 68 % of the whole HTML) for a 132 px-wide offer image. It blocks HTML parsing and cannot be cached or lazy-loaded independently. Export as `offer.jpg` at ~264×352, `loading="lazy"`. `README.md:7-8` still claims all images are embedded; they no longer are. |
| I5 | Shopify SDK (763 KB uncompressed) loaded synchronously and unconditionally | `:441` | Blocks parse near end of body and does nothing until credentials exist. Load with `async`/`defer` (or inject on first CTA interaction) and use `ShopifyBuy.UI.onReady(client).then(...)`. |
| I6 | Two pricing tiers are shown but cannot be selected | `:312-322` (static `.tier` cards), `:454-459` (`contents:{price:false…}`, no `options`) | A single product component with the default (first) variant is mounted. The 2-pack ($49) has no purchase path. Either model Single / 2-Pack as variants and show the option selector, or mount two components with `variantId` under each tier card. |
| I7 | Primary CTA colour fails WCAG AA contrast | `:38` `.btn` white on `#0AA3D6` | 2.91:1 (needs 4.5:1; button text is 17 px/600, not "large"). Also `.tier-badge` (`:138`, 10.9 px, 2.91:1) and `.eyebrow` (`:32`, 11.8 px, `#0993C2` on sand, 3.30:1). Darkening `--cyan` to ≈ `#0A7FA8` (or using navy text on cyan) fixes all three. |
| I8 | Hero video ignores `prefers-reduced-motion` and has no pause control | `:418-422` (hero explicitly exempted), `:423-437` (forces autoplay, strips `controls`) | WCAG 2.2.2 requires a way to pause auto-playing motion longer than 5 s. Reduced-motion users still get a looping video. Respect the media query for the hero and keep `controls` (or add a pause toggle). |
| I9 | Sticky bar is `aria-hidden="true"` while containing a focusable link | `:385-388`, toggled `:406-408` | Fails the axe `aria-hidden-focus` rule; the off-screen link stays in the tab order. Use the `inert` attribute or `visibility:hidden` when hidden. Also no `env(safe-area-inset-bottom)` padding (`:163`) — the button sits under the iPhone home indicator — and no body/footer bottom padding, so the footer is permanently covered on phones. |
| I10 | No canonical, Open Graph, Twitter Card, JSON-LD, `theme-color`, or file-based favicon | `<head>` `:3-11` | Only `title`, `description`, viewport and a data-URI SVG favicon (`:6`). Google SERP favicons and iOS home-screen icons need real files. No `Product` / `FAQPage` / `Organization` structured data. (Draft PR #3 adds all of these.) |
| I11 | Meta description is 233 characters | `:8` | Will be truncated in SERPs (~155–160 chars). |
| I12 | No `robots.txt`, `sitemap.xml`, or `404.html` | live: all return Render's 10-byte plain-text "Not Found" | Add `robots.txt` (allow all + sitemap URL), `sitemap.xml` with the single URL, and a branded `404.html` (Render static sites serve it automatically). |
| I13 | No analytics or conversion tracking of any kind | whole file | There is no GA4, Meta Pixel, TikTok pixel, or Shopify tracking. You cannot measure the funnel at launch. Add with a consent banner if you target EU/UK. |
| I14 | Google Fonts CSS is render-blocking | `:9-11` | Two families × 7 weights. Self-host or subset to 2–3 weights, and/or use the `media="print" onload="this.media='all'"` pattern with a system-font fallback. |
| I15 | `render.yaml` has no custom domain and no headers | `render.yaml:5-9` | Domain is commented out and still says `chillpod.com`. Draft PR #2 fixes the domain; nothing yet adds `Cache-Control`, `Strict-Transport-Security`, `X-Frame-Options`, `Referrer-Policy`. Live response only sends `x-content-type-options`. |

### Nice-to-have

| # | Finding | Where | Notes |
|---|---|---|---|
| N1 | `<h1>` with `<br>` reads as "…Heat.iChillPod Won't…" to crawlers/screen readers | `:206` | Replace `<br>` with a space + `display:block` span. Also 4 lines tall at 375 px (145 px) and 1280 px (235 px). |
| N2 | 2.4 MB of unreferenced media is deployed publicly | `beach-wide.jpg` (244 KB), `chillpod-demo.mp4` (1.28 MB), `cooling.mp4` (782 KB), `cooling-poster.jpg` (110 KB) | Zero references in `index.html`. Delete or move to `design_work/` (already git-ignored). |
| N3 | Header "Buy now" and desktop nav links are 42 px tall | `:57` `.hdr .btn{min-height:42px}`, `:53` `.nav a{padding:9px 15px}` | Slightly under the 44 px touch-target guideline. Everything else (hero 58 px, sticky 46 px, FAQ rows ~64 px) passes. |
| N4 | Sub-12 px text | `.eyebrow` 11.8 px (`:32`), `.badge` 11.8 px (`:104`), `.tier-badge` 10.9 px (`:138`), sticky `small` 10.9 px (`:166`) | Readable-ish, but combined with low contrast (I7) they are the weakest text on the page. |
| N5 | Decorative emoji are read aloud | `:211`, `:237-239`, `:265`, `:269`, `:277`, `:290-295`, `:311` | Wrap in `<span aria-hidden="true">`. |
| N6 | `backdrop-filter` lacks the `-webkit-` prefix | `:46`, `:163` | Safari < 18 shows no blur; falls back gracefully to the rgba background. |
| N7 | `.steps3` wraps to 2 + 1 on phones | `:88-89`, `:181` | 3 × 110 px + gaps > 335 px, so "Go Anywhere Hot" drops to its own row. Cosmetic. |
| N8 | `.tiers` stays two-column between 431–480 px | `:144` | `$49` + `$78` + badge fit, but tightly. Consider stacking ≤ 480 px. |
| N9 | README is stale | `README.md:7-8, 34, 40-41` | Claims images are embedded, references `chillpod.com`, and still says "Replace the Buy Now link". |
| N10 | Countdown/timers have no `aria-live` (good) but the `.countdown` `--:--:--` placeholder flashes before JS | `:211`, `:311` | Minor FOUC. Moot if the timer is removed (C5). |
| N11 | Storefront token will live in the public HTML | `:446` | This is expected for the *public* Storefront token (it is designed to be client-side), but never paste an Admin API or private token here. Keep the note. |

---

## 1) Mobile audit — details

**Viewport meta:** present and correct (`:5` `width=device-width, initial-scale=1.0`). No `maximum-scale` / `user-scalable=no` (good for accessibility).

**Breakpoints:** `≤ 820 px` (`:172-180`: hide nav, single-column hero and proof, show sticky bar), `≤ 480 px` (`:181`: smaller timer, smaller steps), `≤ 430 px` (`:144`: stack tiers), `prefers-reduced-motion` (`:182-187`). There is **no breakpoint that stacks the `.demo` proof cards**, which is the overflow cause (C3).

**Measured results (headless Chromium, mobile emulation):**

| Width | `scrollWidth` | H1 top | Buy-box top | Hero video | Overflowing elements |
|---|---|---|---|---|---|
| 360 × 800 | **459** | 491 | 787 | 240 px square | `.demo`, `.card.pod` (right edge 459), `figure.proof-photo`, `.proof-grid h2`, `.stickybar` |
| 375 × 667 (iPhone SE) | **459** | 506 | 774 | 255 px square | same |
| 390 × 844 (iPhone 14) | **459** | 521 | 753 | 270 px square | same |
| 820 × 1180 | 820 | 710 | 896 | 480 px square | none |
| 1280 × 800 | 1280 | 138 | 496 | 457 px square | none |

**What to verify by hand at 375 px and 390 px after fixes:**
- No horizontal scroll (`document.documentElement.scrollWidth === innerWidth`).
- The sauna photo, "8:00 / 30:00" cards, and the sticky bar's full "Buy now" label are fully visible.
- The price (`$29`) and a Buy CTA are visible in the first viewport (currently they are not on either device).
- The sticky bar clears the iOS home indicator and does not cover the footer's copyright line.
- `.tiers` at 390 px stacks (it does today, `≤ 430 px`), and the "Save $9 · Most popular" badge does not collide with the card border.
- The H1 does not orphan a single word on a fourth line.
- FAQ answers with long `[placeholder]` chips wrap without pushing the `+` icon off-screen (they currently wrap correctly, but only once placeholders are gone will the real answers be testable).
- Landscape 667 × 375: the sticky bar plus 62 px header consume ~130 px; check the hero still shows the headline.

**Touch targets:** hero/offer buttons 58 px, sticky 46 px, FAQ rows ≥ 64 px — pass. Header "Buy now" 42 px and nav links 42 px — marginal (N3).

**Font sizes:** body 16 px, `.sub` 18 px — fine. Four styles under 12 px (N4). `.hero h1` clamps to 33.6 px on phones — good.

**Images:** all external images have `max-width:100%` (`:28`) and `object-fit:cover` with aspect ratios, and are `loading="lazy"` except the hero poster. None have `width`/`height` attributes, so there is layout shift before CSS aspect-ratio applies. `uses-grid.jpg` (1600×893, 258 KB) and `sauna-bg.jpg` (1600×900, 158 KB) are served full-size to phones; add `srcset` or WebP variants (PR #3 adds WebP). `sauna.jpg` is 768×1024 (fine for its ≤ 480 px slot).

**Video:** `aspect-ratio:1/1; object-fit:cover; max-width:480px` (`:78`) — fine visually, but see I2 for weight.

---

## 2) Shopify payment readiness

**What exists (`index.html:440-463`):**
- SDK is loaded from the correct, current CDN URL `https://sdks.shopifycdn.com/buy-button/latest/buybutton.js` (`:441`) — this is Shopify's documented "latest" path. It is loaded synchronously and unconditionally (I5).
- `ShopifyBuy.buildClient({domain, storefrontAccessToken})` and `ShopifyBuy.UI.init(client)` (`:450-451`) are correct API usage for buy-button-js. `UI.onReady(client).then(...)` is the more robust form.
- A `product` component is created with `buttonDestination:'checkout'`, button-only contents, and brand styling (`:454-459`). On success the mailto fallback is hidden (`:460`).
- Mount node `#chillpod-buy-final` (`:323`) and fallback `#chillpod-buy-final-fallback` (`:324`) exist. There is **no** mount in the hero buy box; the hero "Buy now" (`:212`) and header/sticky buttons just scroll to `#offer`.

**What is missing:**
- `SHOP_DOMAIN`, `STOREFRONT_TOKEN`, `PRODUCT_ID` are hard-coded `TODO` strings (`:445-447`). There are no env vars or build step (Render static site, `render.yaml` has no `envVars`), so these must be edited into the file — which is fine for a *public* Storefront token.
- The guard on `:449` returns early, so today: **no button mounts, `ShopifyBuy` is downloaded for nothing, and the mailto fallback is the only CTA.**
- No variant selection for the 2-pack (I6).
- The Shopify store itself (product, payments, shipping, taxes, policies, plan) — none of this can be verified from the repo; the numbered steps in Section C cover every admin screen.

**Can checkout complete today?** No. Even with real credentials pasted in, checkout will fail or be blocked until: the product is published to the Buy Button/custom-app channel, a payment provider is activated, at least one shipping rate exists for the destination, and the store is on a paid plan (trial stores cannot complete real checkouts).

**Credential/setup still needed:** myshopify domain, public Storefront API access token (from the Buy Button channel or a custom app with Storefront API scopes), numeric product ID (and variant IDs if mounting per tier), Shopify Payments (or PayPal/Stripe) activated with business + bank details, shipping rate(s), tax settings, store policies, store name/contact email, paid plan.

---

## 3) Launch readiness checklist

| Check | Status | Detail |
|---|---|---|
| Internal anchors | Pass | `#why`, `#proof`, `#details`, `#offer`, `#uses` all exist; header/nav/sticky links resolve. |
| External resources | Pass (reachable) | Google Fonts ×3, Shopify SDK ×1. No other outbound links — no social, no policies, no contact page. |
| Asset URLs | Pass | `hero-demo.mp4?v=2`, `hero-poster.jpg`, `sauna.jpg?v=2`, `sauna-bg.jpg`, `uses-grid.jpg` all 200 on live. |
| Missing meta | **Fail** | No canonical, OG, Twitter, `theme-color`, `apple-touch-icon`, JSON-LD (I10). Description too long (I11). |
| Structured data | **Fail** | None. Add `Product` (with `Offer`, `priceValidUntil` only if real), `FAQPage`, `Organization`. Do **not** add `AggregateRating` until real reviews exist. |
| Page weight / speed | **Fail** | ~8.7 MB first load: 7.26 MB hero video + 763 KB SDK + ~650 KB images + fonts. LCP is likely the 72 KB poster (OK), but total transfer on cellular is heavy; `preload="auto"` + `autoplay` pulls the whole video. |
| Video format | Needs work | Single H.264 MP4, 1424² @ 4.1 Mbps with a dead audio track; no WebM/AV1 alternative; no mobile rendition (I2). `playsinline muted loop` attributes are correct for iOS autoplay. |
| Image compression | Needs work | `uses-grid.jpg` 258 KB, `sauna-bg.jpg` 158 KB, `sauna.jpg` 135 KB, inline offer JPEG 50 KB (I4). WebP/AVIF at q80 would roughly halve these; PR #3's WebP variants were 25–45 % smaller. |
| Caching | **Fail** | `max-age=0` on all assets (I3). |
| SSL / domain | Pass on `ichillpod.com` | HTTPS 200, valid cert, `http://` → 301 → `https://`, `www` → 301 → apex. `chillpod.com` is **not yours** (S3 bucket, cert mismatch) — remove every reference (C2). No HSTS header. |
| Contact email | **Fail** | `hello@chillpod.com` (`:324`) — wrong domain (C2). Real inbox per PR #2: `ichillpod@gmail.com`. Consider a domain mailbox/forward (`hello@ichillpod.com`) for credibility. |
| FAQ content | **Fail** | 10 placeholders (C4). Remaining answers are short but honest. |
| Claims / legal | **Fail** | Fake timer + reference price (C5); guarantee and free-shipping promises with no policy pages (C6); "Apple & Samsung Support" citation with no link (`:278`); "about twice the temperature your phone is rated for" (`:261`) — 95°F × 2 = 190°F, fine for 200°F but keep it consistent with the actual test footage. |
| Other embarrassments | | Yellow dashed `[TBC]` chips; "Bu…" truncated sticky button on every phone; 8 vs 30 cards half off-screen; README says "chillpod.com"; unused demo videos publicly downloadable (N2); no way to contact the company except the wrong email. |

---

## 4) Redesign variations (proposals only — not implemented)

Research notes that informed these (brief web research, Sept 2026): top-converting DTC product pages put the packshot/product-in-use and **one** value claim above the fold, put social proof in the first viewport, cluster trust signals within ~300 px of the CTA, use bundle/anchor pricing, and rely on a sticky thumb-reachable CTA on mobile. Outdoor-gear buyers respond to specific field-test numbers (temperatures, durations, ratings) over generic badges. The closest competitor, PHOOZY, sells a passive insulating pouch at $22–50 with a fit/size table and a "we don't cool your phone, we slow heating" FAQ — iChillPod's active-cooling claim and real sauna footage are its sharpest differentiators against that.

### Variation 1 — "Sauna Lab" (proof-first, field-test aesthetic)

- **Visual concept:** Dark charcoal/navy base (`#0B1520` → `#0B2A4A`) with a heat-map accent pair: coral/amber (`#FF6B5A` → `#FFB347`) for "bare phone" and ice cyan (`#6FD9FF`) for "in iChillPod". Typography: Space Grotesk for oversized numerals (72–120 px timers, temperatures), a mono face (JetBrains Mono / IBM Plex Mono) for spec labels, Figtree for body. Layout: full-bleed, edge-to-edge sections, thin hairline rules, data-viz motifs (temperature curves, thermometer bars, timestamps burned into video).
- **Hero:** Split-screen side-by-side loop: bare phone hitting the thermal-shutdown screen at 8:00 on the left, phone in iChillPod still recording at 30:00 on the right, with a live-updating temperature/time overlay. Headline: "200°F sauna. 8 minutes bare. 30 minutes in iChillPod." Sub: "The only phone cooler that pulls heat *out*." Price + Buy directly under the headline on mobile; the video sits behind/beside it, not above it.
- **Product section:** Cutaway render of the frozen core with conduction arrows; a spec sheet laid out like a lab card (fit range, freeze time, runtime, weight, condensation note) — every cell filled with a real number; a three-column comparison (insulated pouch / ice-pack case / iChillPod) that pre-empts "isn't this just a pouch?".
- **CTA placement:** Buy in hero, a "Buy" cell at the bottom of the spec card, tier cards that *are* the buttons (Single / 2-Pack), sticky bottom bar with price. One CTA verb everywhere ("Get iChillPod").
- **Why it converts better:** The brand's single strongest asset is a real, repeatable test; this direction makes the test the entire visual language, which matches how outdoor/gear buyers evaluate (specific numbers, not vibes). It also visually separates iChillPod from PHOOZY-style pouches. Risk: darker palette needs careful contrast; keep body text ≥ 7:1.

### Variation 2 — "Summer Kit" (bright lifestyle, ad-continuity)

- **Visual concept:** Sun-bleached palette — sand (`#FBF7F0`), pool blue (`#0AA3D6` darkened to ≈ `#0A7FA8` for text/buttons), coral (`#FF6B5A`), a warm yellow highlight. Rounded, friendly geometric sans (Figtree or Outfit) throughout; large, warm lifestyle photography per scene (beach, golf cart, sidelines, festival, sauna) with the phone visibly inside the pod. Layout: alternating full-bleed photo bands and short copy blocks, big rounded cards, generous white space.
- **Hero:** Full-width lifestyle photo/video (beach, phone sliding into the pod), headline "Keep filming at 100°F." Sub: "Freeze it, slide your phone in, go anywhere hot." Under the headline: star row + "★★★★★ 'Saved my phone at my kid's tournament' — first-name, state" (only once real reviews exist; use "Founder-tested in a 200°F sauna" until then). Price, "Free shipping · 30-day guarantee", Buy — all in the first viewport on 375 px. Ad-to-hero continuity: the hero image should be the same creative as the Meta/TikTok ad.
- **Product section:** "A day with iChillPod" horizontal story (freeze overnight → pack → swap in the 2-pack → wipe condensation) leading into the offer; product shot carousel (front, slot, core, in-hand for scale); 2-pack framed as "One's always frozen" with the Save $ badge.
- **CTA placement:** Hero, after the scene band ("Which one's your summer?" → Buy), offer card, sticky bar with price and a tiny guarantee line.
- **Why it converts better:** Impulse/emotional purchase at $29 is driven by imagining the moment (kid's game, beach video). Lifestyle continuity between ad and page is one of the most consistent conversion patterns for Meta/TikTok traffic, and it lets the 2-pack story ("one always frozen") carry the AOV. Risk: needs real photography (current lifestyle shots look AI-generated; buyers notice).

### Variation 3 — "Cold Hard Facts" (premium tech-accessory minimal)

- **Visual concept:** Near-white/ice base (`#F7FAFC`), graphite text (`#101820`), one electric-cyan accent used only for the buy button and key numbers. Typography: a tight grotesk (Inter Tight / Söhne-like) with very large product headlines and small uppercase mono labels. Layout: Apple/Peak-Design cadence — one idea per screen, huge product renders on white, scroll-driven "how it works" (three frames: frozen core, phone slides in, heat arrows out). Minimal chrome, no emoji, no badges, no timers.
- **Hero:** Clean packshot of the pod with a phone half-inserted, headline "The phone cooler that actually cools." One-line sub with the mechanism ("A frozen core pulls heat out by direct contact — no power, no batteries"). Price, Buy, and "Fits iPhone 12–17 and Galaxy S22–S25 (with case)" on the same line — compatibility is the #1 accessory objection.
- **Product section:** Tech-spec table (dimensions, weight, freeze time, runtime, material, condensation guidance) side-by-side with the comparison table; "In the box"; a short founder/engineering note with a photo (3–4 sentences) explaining why insulation isn't enough.
- **CTA placement:** Hero, repeated after the spec table, sticky bar; single clean checkout button styled to match Shopify's Shop Pay/Apple Pay so express checkout appears native.
- **Why it converts better:** Positions a $29–49 item as a considered, engineered gadget rather than a novelty, which supports the 2-pack price and reduces "is this a gimmick?" hesitation. Very light page (fast on cellular) and the compatibility line up front kills the top objection. Risk: colder tone may under-perform for impulse beach-bag buyers versus Variation 2; strongest for Google Search / comparison-shopping traffic.

**Suggested test plan (proposal only):** ship Variation 2 for paid social traffic and Variation 3 for search traffic, borrowing Variation 1's split-screen proof module in both.

---

## 5) Other improvements

**SEO**
- Add canonical, OG/Twitter (1200×630 image), `theme-color`, real favicon files, JSON-LD `Product` + `FAQPage` + `Organization` (I10).
- Trim the description to ≤ 155 chars; lead with the search intent ("phone cooler", "phone overheating at the beach"). See the keyword research in draft PR #1 (`docs/seo-keyword-research.md`).
- Fix the `<h1>` `<br>` join (N1). Add `robots.txt` + `sitemap.xml` (I12). Consider a lightweight `/faq` or `/how-it-works` page later so long-tail queries have a landing target.
- Add `width`/`height` on `<img>` to remove CLS.

**Trust signals**
- Footer links: Refund policy, Privacy, Terms, Shipping, Contact (with a real address or at least a real email). Shopify will host these; link to them.
- Guarantee badge and "Secure checkout · Shop Pay / Apple Pay / Google Pay" logos within 300 px of the buy button (real once Shopify Payments is on).
- "Founder-tested" block with a real photo and 3–4 sentences; sauna footage is already the proof — put a timestamped still from it next to the guarantee.
- Replace AI-looking lifestyle imagery with real photos/UGC as soon as units exist.

**Social proof**
- None exists yet; do not fabricate stars or counts. Collect 5–10 real reviews via a launch batch (friends/family/beta) with photos, then add a curated "proof module" (short quote + first name + city + photo) near the CTA and `AggregateRating` JSON-LD.
- Add a short UGC-style vertical video strip (2–4 s clips, muted) once available.

**FAQ additions (real customer objections)**
- Does it fit with a case / MagSafe / PopSocket? (give internal slot dimensions).
- Can I use my phone while it's inside? Can I hear calls / see the screen?
- How long does it take to freeze? Can I leave it in the freezer permanently?
- Is cold or condensation bad for my phone? (Apple warns about condensation — give explicit "wipe before pocketing, don't submerge" guidance and mention the 32–95°F operating range with a link.)
- What is the core made of? Is it non-toxic if it leaks? Does it float?
- Can I fly with it / is it TSA-friendly?
- Warranty and what happens if the shell cracks.

**Accessibility**
- CTA contrast (I7), hero video pause/reduced-motion (I8), sticky bar `aria-hidden`/`inert` (I9), decorative emoji `aria-hidden` (N5), skip-link optional, `<video>` should have a text alternative beyond `aria-label` (short caption of what happens is already present — good).

**Performance wins (ordered by impact)**
1. Re-encode hero video (−5 MB) and add WebM source; `preload="metadata"` with poster if autoplay is dropped on cellular.
2. Long-lived cache headers via `render.yaml` (`headers:`).
3. Defer/async Shopify SDK; consider loading only on CTA hover/tap.
4. Externalize the base64 offer image; WebP for the four JPEGs; `srcset` for `uses-grid`.
5. Subset/self-host fonts or make the Google Fonts stylesheet non-blocking.
6. Delete unused media from the deploy (N2).

**Ops / measurement**
- Add GA4 (or Plausible) + Meta Pixel + Shopify's Buy Button attribution; verify "Purchase" events fire from the Shopify thank-you page (needs Shopify's customer-events pixel).
- Set up Search Console with the sitemap; watch for the `chillpod.com` typo in any ad copy.
- Add security headers in `render.yaml` (`Strict-Transport-Security`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`).

---

## C) Shopify connection steps — from current state to a working checkout

All admin paths are relative to `https://admin.shopify.com/store/<your-store>/`.

1. **Store basics** — `Settings → General`: store name "iChillPod", store contact email `ichillpod@gmail.com`, currency USD, timezone. `Settings → Notifications → Sender email`: set and verify the sender.
2. **Pick a paid plan** — `Settings → Plan`. Trial stores cannot complete real checkouts; Basic is sufficient for a Buy Button.
3. **Create the product** — `Products → Add product`: title "iChillPod Phone Cooler", description, images. Add a **variant option** "Pack" with values `Single` and `2-Pack`. Prices: Single **$29.00** (leave *Compare-at* empty unless $39 was a genuine prior selling price — see C5), 2-Pack **$49.00**. Set inventory/SKU, weight (needed for shipping), and mark **Physical product**. Note the numeric **product ID** at the end of the product URL (`/products/1234567890123`) and each **variant ID** (`Variants → ⋮ → Edit → URL`, or via `.../products/<id>.json`).
4. **Install the Buy Button channel** — `Settings → Apps and sales channels → Shopify App Store → "Buy Button" → Add app` (free).
5. **Publish the product to the channel** — on the product page, `Sales channels and apps → Manage → tick "Buy Button"` (and "Online Store" if you ever use it). Products not published to the channel return "not found" in the SDK.
6. **Get the Storefront access token and domain** — `Buy Button channel → Create a Buy Button → Product → iChillPod → Next → Copy code`. In the generated snippet copy `domain: 'xxxx.myshopify.com'` and `storefrontAccessToken: '…'`. (Alternative: `Settings → Apps and sales channels → Develop apps → Create an app → Configure Storefront API scopes → tick unauthenticated_read_product_listings, unauthenticated_write_checkouts, unauthenticated_read_checkouts → Install → API credentials → Storefront API access token`, then publish the product to that app in step 5.) This is the **public** token; it is safe in HTML. Never use an Admin API token.
7. **Paste credentials into `index.html:445-447`** — `SHOP_DOMAIN`, `STOREFRONT_TOKEN`, `PRODUCT_ID` (numeric string, e.g. `'1234567890123'`). Also change `:324` to `mailto:ichillpod@gmail.com`.
8. **Wire the two tiers (I6)** — either (a) set `options.product.contents.options:true` so the SDK renders the Single/2-Pack selector, or (b) create two mounts (`#buy-single`, `#buy-2pack`) inside the tier cards (`:313-321`) and call `ui.createComponent('product', { id: PRODUCT_ID, variantId: '<variant id>', node, options })` for each. Also add a mount in the hero buy box so the hero "Buy now" (`:212`) can become a real checkout button.
9. **Checkout behaviour** — keep `buttonDestination:'checkout'`. Buy-button-js opens checkout in a new window by default; set the checkout `popup` option to `false` (see buy-button-js "Checkout" options) so iOS Safari popup blockers don't swallow the tap, and test on a real iPhone.
10. **Activate payments** — `Settings → Payments → Shopify Payments → Activate`: business type, EIN/SSN, address, DOB, bank account. Enable Shop Pay, Apple Pay, Google Pay (accelerated checkouts). Optionally add PayPal as a secondary provider. Use `Shopify Payments → Manage → Test mode` for step 15 and **turn it off before launch**.
11. **Shipping** — `Settings → Shipping and delivery → General shipping rates → Manage → Add rate`: "Free shipping", price $0, condition "Order price ≥ $0" for United States (add other countries only if you will actually ship there — otherwise checkout will say "doesn't ship to this address"). Set the product weight so carrier-calculated rates work later.
12. **Taxes** — `Settings → Taxes and duties → United States → Collect sales tax` for the states where you have nexus; leave prices tax-exclusive or tick "include tax in prices" consistently with the $29/$49 shown on the site.
13. **Policies** — `Settings → Policies`: Refund policy (must say 30-day money-back to match the site), Privacy policy, Terms of service, Shipping policy, Contact information. Then link these URLs from the site footer (C6). `Settings → Checkout`: require email, decide phone optional, marketing consent checkbox.
14. **Branding** — `Settings → Brand`: logo, `#0AA3D6` accent, so the checkout page matches the site. Optional but recommended: `Settings → Domains → Connect existing domain → shop.ichillpod.com` (CNAME to `shops.myshopify.com`) and make it primary so checkout URLs read `shop.ichillpod.com/checkouts/…` instead of `xxxx.myshopify.com`.
15. **Test** — with Test mode on, load `ichillpod.com`, confirm the Shopify button replaces the mailto fallback, buy Single and 2-Pack with test card `4242 4242 4242 4242`, confirm both orders in `Orders`, confirm the customer email arrives. Turn Test mode off, place one real order, and refund it from `Orders → Refund`.
16. **Deploy** — commit `index.html`, push `main`; Render auto-deploys (`render.yaml`). Purge Cloudflare/Render cache if the old HTML is still served (`s-maxage=300`, so wait ≤ 5 minutes).
17. **Measure** — `Settings → Customer events` (Shopify pixel) or a GA4/Meta pixel on both the site and checkout so purchases are attributed.

---

## D) Branch and PR

- **Branch:** `cursor/launch-readiness-audit-8ada`
- **Draft PR:** https://github.com/goldexchangev-hash/chillpod/pull/6 (draft, unmerged). It contains only this report — no product code changes.

---

## Relationship to existing draft PRs (not merged, not modified by this audit)

| PR | Branch | Overlap with this audit |
|---|---|---|
| #1 `docs: iChillPod SEO keyword research & competitive analysis` | `cursor/seo-keyword-research-e273` | Research only; complements Section 5 SEO. |
| #2 `Configure ichillpod.com as the Render custom domain` | `cursor/ichillpod-custom-domain-7712` | Fixes C2 (`mailto:ichillpod@gmail.com`), I15 (domains in `render.yaml`), N9 (README), adds `DOMAIN.md`. The live site already resolves correctly, so the DNS part appears done; the `render.yaml`/email/README parts are still only in the draft. |
| #3 `Landing page: SEO head, pre-order CTAs, FAQ, image perf and mobile fixes` | `cursor/landing-page-seo-conversion-polish-ab63` | Addresses C3 (stacks proof cards ≤ 640 px and reports `scrollWidth === innerWidth` at 360–1280), C4 (removes all placeholders — but check that its replacement FAQ copy contains real, owner-confirmed numbers before merging), I1 (headline-first hero), I4/I10/I11 (OG, JSON-LD, WebP, favicons, `width`/`height`), I9 partly (safe-area padding), N1. It leaves C5 (fake timer) in place and flags it. It does **not** touch C1 (Shopify credentials), I2 (video weight), I3 (cache headers), I5, I6, I7, I8, I13, I14. |

Recommendation for the owner: review and merge #2 and #3 (after confirming the FAQ facts in #3), then work Critical items C1, C5, C6 and Important items I2, I3, I6, I7, I8 in that order. This audit deliberately does not implement any of them.
