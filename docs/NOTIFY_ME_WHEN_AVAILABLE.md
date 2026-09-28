# "Notify me when available" on ichillpod.com — waitlist + automatic back-in-stock email (reversible)

**Nothing in this repo changes the live store.** ichillpod.com is a Shopify **Dawn** theme; this
GitHub repo is only the legacy static Render landing page (`index.html`). Merging this PR does
**not** add a waitlist, store an email, or send anything. Every step below is done by a human in
**Shopify Admin**. No step is destructive; the full revert is in §9.

Companion runbook: [`COMING_SOON_DISABLE_ORDERS.md`](COMING_SOON_DISABLE_ORDERS.md) (draft
[PR #18](https://github.com/goldexchangev-hash/chillpod/pull/18) — the file lives on that branch
until it merges). Coming Soon mode (inventory 0, *continue selling* off, "Sold out" → "Coming soon")
stays exactly as it is. **This plan does not raise inventory.**

---

## 0. Decision in one paragraph

Install one dedicated **Back in Stock / "Notify me" app** from the Shopify App Store
(recommended: **STOQ**; alternatives: **Amp Back in Stock**, **Notify Me!** — all three are
*Built for Shopify*, use a **theme app embed** so no theme files are edited, show the button only
while the variant is unavailable, and **email the waitlist automatically the moment inventory goes
above 0**, with a link to `https://ichillpod.com/products/chillpod`). Shopify itself has no native
"email me when back in stock" feature: Shopify Email has no restock automation, Shopify Flow can
detect the inventory change but cannot email a waitlist, and a theme-only form stores emails but
never sends anything. Building webhooks + email in this static repo is the wrong stack for the live
Dawn store.

The one thing to plan around: **every free tier caps notifications per month (10–30)**. The
waitlist for a single-SKU launch will likely exceed that, so budget ~$10 for the month you restock
(§6).

---

## 1. Live state (read-only check, 2026-09-28)

| | |
| --- | --- |
| Storefront / shop | https://ichillpod.com — `yz0m1m-ru.myshopify.com` (`ichillpod.myshopify.com` 301s to it) |
| Live theme | **Dawn — payment icons preview**, Dawn schema **16.0.0**, theme id `188025995375`, role `main`. Online Store 2.0 → supports **app embeds** and **app blocks**. |
| Product | handle `chillpod`, product `15554226356335`, single variant **`67578266419311`**, **$29.95**, status Active |
| Inventory | `inventory_management: "shopify"` (Track quantity **on**), quantity **0**, *Continue selling when out of stock* **off** → `available: false`. **Leave as is.** |
| PDP buy area | `<button class="product-form__submit …" disabled><span>Coming soon </span>` (label still has a **trailing space** — cosmetic, see PR #18 §2), Shop Pay accelerated checkout disabled, payment-icon row below (a **local edit** in `snippets/buy-buttons.liquid` — the live theme is not stock Dawn). |
| Back-in-stock tooling | **None installed.** No app embeds / `cdn.shopify.com/extensions/…` scripts in the PDP, homepage, or `/collections/all` HTML. No Klaviyo/Omnisend/Mailchimp scripts. |
| Where the product is shown | Homepage: 6 CTAs (hero, featured CTA, FAQ, sticky bar, header "Buy Now") — **all link to `/products/chillpod`**; there is **no** featured-product or collection section. Header menu: Home / Buy Now / FAQ / Contact. `/collections/all` exists but nothing links to it. → **The PDP is the only surface that needs the button.** |

---

## 2. How this interacts with Coming Soon

- The apps show "Notify me" **because** the variant is unavailable — Coming Soon mode is exactly
  the state they are designed for. Nothing about the inventory hard stop changes.
- The disabled **"Coming soon"** button stays. The app adds its own button/form **directly below
  it** (app embed inline placement) or where you drop the app block. Do not hide or relabel the
  Dawn button; the app hides itself automatically once stock is back and "Buy Now" returns.
- **Do not raise inventory to test.** Setting quantity > 0 — even for a minute — (a) opens
  checkout to the public and (b) fires the restock emails to everyone on the waitlist. Every app
  below has a **"send test email"** that does not need a restock (§5 step 8).
- When you *are* ready to sell: restock (§6) → emails fire automatically → optionally restore
  the "Sold out" locale string per the Coming Soon runbook §6 (not urgent; it isn't rendered
  while in stock).

---

## 3. Primary path — a dedicated Back in Stock app (verified against App Store listings 2026-09-28)

All three: *Built for Shopify* badge, free plan, Online Store 2.0 **theme app embed** (toggle in
the theme editor, **no Liquid files edited**), button shown only when the variant is unavailable,
customizable button text, **automatic** email on inventory > 0 with product link, test email
without restocking, clean uninstall.

| | **STOQ** — *Preorder, Back In Stock ‑ STOQ* (Artos Software) | **Amp Back in Stock & Preorder +** (HEL / Amp, since 2011) | **Notify Me! Back in Stock Alert** (Notify Me!) |
| --- | --- | --- | --- |
| Listing | https://apps.shopify.com/back-in-stock-restock-alerts | https://apps.shopify.com/back-in-stock | https://apps.shopify.com/preorder-back-in-stock |
| Rating | **5.0** (3,741) | 4.9 (947) | 4.9 (3,829) |
| **Free tier** | **30 emails / month**, unlimited registrations, automatic restock alerts, Notify-me widget, 24/7 chat. STOQ branding on widget/emails. | **10 notifications / month**, unlimited registrations, Notify Me button + form. | "Lite": **10 restock notifications** (period not stated on listing — confirm in-app), 5 preorders. |
| First paid tier (for restock month) | **Lite $10/mo** — 1,000 email/SMS per month, removes branding, 14-day trial | Starter **$19/mo** — 500 notifications/month, 14-day trial | Kickstart **$9.90/mo** — 500 alerts, 7-day trial ($3.96 first month) |
| Default button label | "Notify me when available" (editable) | editable | editable |
| Storefront placement | App embed (inline under the sold-out button), Embedded form or Button + Popup | App embed + optional **app block** (drag-position in theme editor) + auto inline | App embed / blocks; collection-page widget only on **Standard $39.90** |
| Test without restocking | **Yes, documented** — *Customize email → Send test email* | Template preview / test send (confirm in-app before relying on it) | Not stated on listing — confirm in-app; otherwise use the hidden-test-product method (§5 step 8) |
| Docs used | help.stoqapp.com (*Enable STOQ on your theme*, *Test your STOQ setup*, *Set up alerts*) | help.useamp.com (*Product Page Button Setup*) | listing only |

**Recommendation: STOQ.** Highest rating with the largest review base, the most generous free tier
(30 vs 10), the cheapest meaningful paid month ($10 → 1,000 emails), and its default label already
matches the requested copy. Amp is the longest-running and fine if you prefer it (its free cap is
the tightest). Notify Me! is equally capable; its listing is vaguer about the free cap.

**Ruled out:** *ReStocked* (WaveTech, apps.shopify.com/restocked) — 0 reviews, launched 2025, not
Built for Shopify. Klaviyo/Omnisend back-in-stock flows — only worth it if the store already runs
that ESP (it does not today; no scripts present).

Theme-only / Shopify-native options are **not** primary because none auto-sends on restock
(§7).

---

## 4. Admin-only vs. this repo

| Must be done in Shopify Admin (cannot be done by merging this PR) | Done in this repo |
| --- | --- |
| Install the app; accept its data-access scopes | Nothing that affects the store |
| Turn on the app embed on the **live** theme (`Dawn — payment icons preview`) and Save | (optional) keep this runbook + the fallback snippet |
| Set button text, form fields, consent copy | |
| Configure the restock email template (product link) | |
| Test signup + test send | |
| Restock day: check plan cap → raise inventory | |

---

## 5. Exact steps — STOQ (labels from STOQ's help center; Amp / Notify Me! are the same shape)

Prerequisites: staff account with **Apps** and **Themes** permissions. Have a throwaway email you
can read (e.g. `you+chillpod@…`). **Do not touch Products → Inventory at any point in this section.**

1. **Install.** Shopify Admin → **Apps** → *Shopify App Store* → search **STOQ** (or open
   https://apps.shopify.com/back-in-stock-restock-alerts) → **Install** → review scopes (it asks
   for customers, products/inventory, orders, theme, script tags — expected for this app class;
   see §10) → **Install app**. Free plan; no card needed.
2. **Open the Back in stock module.** In the STOQ app → **Back in stock alerts** → tab **Settings**
   (sub-tabs *Signup widget*, *Notifications*, *Delivery settings*, *Integrations*).
3. **Enable the widget.** *Signup widget* → widget status card → **Enable** (status → *Active now*).
   Pick form type **Button + Popup** (keeps the PDP layout untouched; the button sits under the
   disabled "Coming soon" button and opens a small email form) — or **Embedded** if you prefer the
   email field inline.
4. **Turn on the app embed on the live theme.** A banner *App embed is disabled* appears → click
   **Enable app embed** → STOQ opens the theme editor with *App embeds* open → toggle **STOQ** on →
   **Save** (top right). Manual route: Online Store → Themes → live theme → **Customize** → left
   rail, third icon (**App embeds**) → **STOQ** on → Save. The embed is **per theme**; if a new theme
   is published later, repeat this.
   *(Amp: also enable **Back in stock helper** in App embeds; optionally Product template → Add block
   → Apps → **Back in Stock button**, drag it directly under **Buy buttons**.)*
5. **Button copy and look.** *Signup widget* → **Customize widget** → text **`Notify me when
   available`**; colors to match Dawn's secondary button (the "Coming soon" button is
   `button--secondary`: outlined, brand text color); form fields **email only** (no phone — SMS
   costs extra and needs carrier verification); success message e.g. *"Thanks — we'll email you the
   moment the iChillPod is available."* Save.
6. **Which products.** *Products* tab → confirm **iChillPod** (`chillpod`) is listed with the widget
   active. Default eligibility = every out-of-stock variant, which is just this one. Leave defaults.
7. **Restock email.** *Notifications* → **Email** channel on (default) → *Customize email*:
   - Sender: the store's sender email (Settings → Notifications → **Sender email** should be a
     domain you control, e.g. `hello@ichillpod.com`, with SPF/DKIM verified — otherwise expect
     spam-foldering; not required to *work*, required to *land*).
   - Subject e.g. **"iChillPod is available — grab yours"**.
   - Body: include the product image/title variable and a button whose link is the product URL.
     STOQ inserts the product link variable by default; if you hard-code it use
     **`https://ichillpod.com/products/chillpod`** (the `*.myshopify.com` URL also works — it
     301s to ichillpod.com).
   - Sending: **Automatic** (default). Batched/scheduled delivery is a paid feature; not needed.
8. **Test — without restocking.**
   - In the same *Customize email* preview → **Send test email** → your throwaway address → check
     it lands and the button opens the PDP.
   - Private browser window → https://ichillpod.com/products/chillpod → the **Notify me when
     available** button is under the "Coming soon" button → submit your throwaway email → success
     message → STOQ *Products* tab shows 1 signup.
   - Verify `curl -s https://ichillpod.com/products/chillpod.js | grep -o '"available":[a-z]*'`
     still prints `"available":false` (nothing you did changed inventory).
   - Delete your test signup afterwards (*Manage customers*) or leave it — it costs one of the
     free-tier emails on restock day.
   - **If you must see a real restock email end-to-end**, do it on a **draft duplicate theme** for
     the button, and for the email create a **hidden test product** (Draft status or unpublished
     from Online Store), set *its* inventory 0 → sign up → set it to 1 → email arrives → set back to
     0. **Never do this on the iChillPod product.** (STOQ's own test guide uses a test product for
     this reason.)
9. **Consent copy.** In the form, keep the default line about receiving one email about this
   product. If you sell into the EU/UK/Canada, turn on **double opt-in** in the widget settings
   (§10). Signups are stored in STOQ's waitlist; optionally enable "create customer / add to
   Shopify email subscribers" in *Integrations* if you want them in Shopify's customer list too
   (then they also appear under Customers with marketing consent — reversible per customer, do not
   bulk-delete customers).

Done. From here the storefront shows the button on every PDP visit while the variant is
unavailable, signups accumulate at zero cost, and no email goes out until inventory > 0.

---

## 6. Restock day — this is the step that opens sales (read fully first)

**Raising inventory above 0 simultaneously (1) re-enables Buy Now / Shop Pay / checkout for the
public and (2) fires the back-in-stock emails to the entire waitlist within ~1–2 minutes.** It is
reversible (set it back to 0) but sent emails cannot be recalled. Do it only when you can ship.

1. STOQ → *Back in stock alerts* → **Overview / Products** → note the **waitlist size** for
   iChillPod.
2. Compare to your plan's monthly cap: Free = **30 emails** (Amp 10, Notify Me! 10). If the
   waitlist is larger, **upgrade first** (STOQ **Lite $10/mo** → 1,000 emails; 14-day trial may
   cover it) so the send isn't truncated. Anything over the cap either queues or is not sent,
   depending on the app — don't find out with real customers.
3. (Optional) Pause any abandoned-checkout / marketing automations you paused for Coming Soon —
   re-enable them now.
4. Admin → **Products → iChillPod → Inventory** → set **Available** to the real count at each
   location → **Save**. Keep *Track quantity* on so the app can see future sell-outs (the Coming
   Soon runbook records that the pre-launch state was *not tracked*; choose deliberately).
5. Within a couple of minutes: `…/products/chillpod.js` → `"available":true`; PDP shows **Buy
   Now**, Shop Pay visible, **Notify me button gone**; STOQ *Reports* shows notifications sent;
   your own test address (if still on the list) received the email; link opens the PDP.
6. After the launch month, **downgrade** back to Free if you upgraded.
7. Optional, later: restore `products.product.sold_out` → **Sold out** per the Coming Soon runbook
   §6 so the next genuine sell-out reads correctly. Also trim the trailing space if not already.

If you sell out again later, the same setup keeps working with no action: button reappears at 0,
emails fire at the next restock.

---

## 7. Fallbacks (documented, **not** recommended as primary)

### 7a. Shopify Forms + customer tag + Shopify Email (no third-party app; **manual** send)

- **Shopify Forms** (free, Shopify-made): create an *inline* form, place it on the product
  template via *Add block → Apps → Forms*, field: email, tag **`chillpod-waitlist`**, consent
  text. Signups become **Customers** with email-marketing consent. Caveat: Forms does **not** know
  about availability — it shows regardless of stock, so you must remove/hide the block yourself on
  restock day.
- **Send on restock:** Shopify Email → *Create campaign* → recipients = segment
  `customer_tags CONTAINS 'chillpod-waitlist'` → product block linking to
  `https://ichillpod.com/products/chillpod` → send **manually** right after raising inventory.
  Shopify Email includes 10,000 free emails/month, so caps are not an issue.
- **Why not automatic:** Shopify Flow has the trigger *Inventory quantity changed* but cannot
  email a list from it — *Send marketing email* is a customer-context action, *Get customer data*
  returns at most 100 records, and looping/batching hits Flow run limits. You can wire Flow to
  send **you** an internal reminder to press Send; that's the honest ceiling. More DIY, weaker
  analytics (no per-product waitlist, no "sent/converted" report), no auto-hide when in stock.

### 7b. Dawn Custom Liquid block (zero apps; **storage only**)

[`theme-patches/dawn/notify-me-fallback/notify-me-customer-form.liquid`](../theme-patches/dawn/notify-me-fallback/notify-me-customer-form.liquid)
is a paste-ready snippet: Theme editor → **Products → Default product** → section **Product
information** → *Add block* → **Custom Liquid** → paste → drag directly under **Buy buttons** →
Save. It renders **only while `product.available` is false**, posts to Shopify's built-in
`{% form 'customer' %}` (the same mechanism as Dawn's newsletter block), and creates a customer
with email-marketing consent tagged **`chillpod-waitlist`**. It is stored in that theme's
`templates/product.json` — **no theme code files are edited**; removing the block is the whole
revert. It **never sends an email**: you still send the Shopify Email campaign in 7a. Use it only
if installing any app is off the table. Because the live `buy-buttons.liquid` already carries a
local edit (payment-icon row), prefer this editor block over touching that snippet.

### 7c. Klaviyo / Omnisend back-in-stock flows

Only if the store adopts one of these ESPs for other reasons. Klaviyo's BIS flow needs its
onsite JS + a theme snippet and a paid plan for meaningful volume; STOQ and Amp can sync to
Klaviyo later if that day comes. Not today.

---

## 8. Verification checklist (after §5, before any restock)

- [ ] PDP HTML now loads an app embed: `curl -s https://ichillpod.com/products/chillpod | grep -c 'cdn.shopify.com/extensions'` → `≥ 1` (was `0` on 2026-09-28).
- [ ] Private window → PDP → **Notify me when available** visible under the disabled **Coming soon** button; Dawn button, price, payment icons, gallery unchanged.
- [ ] Submit throwaway email → success state; entry visible in the app's waitlist/Products tab.
- [ ] *Send test email* received; CTA opens `https://ichillpod.com/products/chillpod`.
- [ ] `curl -s https://ichillpod.com/products/chillpod.js | grep -o '"available":[a-z]*' | head -1` → still `"available":false`.
- [ ] `curl -s -o /dev/null -w '%{http_code}\n' -X POST -d 'id=67578266419311&quantity=1' https://ichillpod.com/cart/add.js` → still `422`.
- [ ] Admin → Orders: no new orders.
- [ ] Homepage / `/collections/all`: unchanged (no widget expected there; all CTAs still go to the PDP).
- [ ] Online Store → Themes → live theme → *Edit code*: no modified `.liquid` files from this work (only the app embed toggle, stored in `config/settings_data.json`).

---

## 9. Revert — exact steps (none destructive)

1. **Stop new signups, keep data:** STOQ → *Back in stock alerts → Settings → Signup widget* →
   **Disable**. Button disappears; waitlist intact.
2. **Remove from theme:** Theme editor → *App embeds* → **STOQ** off → Save. (Amp: also delete the
   *Back in Stock button* app block if you added one.) No Liquid files to restore.
3. **Export the waitlist first** if you want it (app *Reports/Products* → export CSV).
4. **Uninstall:** Admin → Apps → STOQ → **Uninstall**. Shopify sends the app a mandatory
   data-erasure webhook **48 hours** after uninstall; the waitlist is gone after that per the app's
   privacy policy. Customers the app created in Shopify (if you enabled that sync) **remain** —
   leave them; do not bulk-delete customers.
5. Cancel any paid plan by uninstalling or downgrading in-app; Shopify prorates app charges.
6. Fallback 7b: theme editor → Product information → remove the Custom Liquid block → Save.
7. Storefront / this repo: nothing to revert; neither was changed.

Inventory and the Coming Soon locale strings are untouched by this feature; their revert is in the
Coming Soon runbook §6.

---

## 10. Flags and risks — read before applying live

- **Raising inventory is the sales-opening, email-firing step (§6).** Everything else in this plan
  is inert. Never restock the iChillPod product "just to test".
- **Free-tier caps:** STOQ 30 / Amp 10 / Notify Me! 10 notifications per month. A launch waitlist
  will exceed these. Budget one paid month (~$10–19) *before* restocking; check overage terms
  (STOQ Lite: $0.025/SMS — email is within the 1,000 cap).
- **Marketing consent:** the button collects email for a *transactional-ish* single notification,
  but apps store it as marketing consent when synced to Shopify. If you sell to EU/UK/Canada,
  enable **double opt-in** and keep the consent sentence in the form. Only one restock email is
  sent per signup; follow-up/reminder emails are optional features — leave them off unless wanted.
- **App permissions:** all three request read/write on customers, products/inventory, orders and
  the theme (normal for this category). They **read** inventory; they should not *write* it —
  do not enable any "auto-preorder" or "continue selling" feature in the app while in Coming Soon.
- **Preorder features:** STOQ / Amp / Notify Me! also sell preorders. **Do not create a preorder
  offer** — that would let customers pay now, which is exactly what Coming Soon mode prevents.
- **Deliverability:** verify the sender domain (SPF/DKIM) under Settings → Notifications before
  restock day, or the one email that matters lands in spam.
- **App embed is per theme:** publishing a different theme drops it — harmless, re-toggle.
- **Never delete** the product, variant, media, customers, or the theme. Duplicate the live theme
  before any theme-editor work so the previous state is one click away (**Themes → ⋯ → Duplicate**).
- **Abandoned-checkout / marketing automations** paused for Coming Soon: re-enable on restock day,
  not before.
- **Channel lag:** Shop / Google / Meta reflect availability hours later; the app keys off Shopify
  inventory webhooks and reacts in minutes.
- **The trailing space** in the "Coming soon" label is still live — cosmetic, tracked in PR #18.

---

## 11. What this PR does and does not do

- Adds this runbook and one optional fallback Liquid snippet. **No changes** to `index.html`,
  `render.yaml`, or `README.md`; the Render deploy is unaffected.
- Does **not** install anything, change inventory, or alter the live theme. **Draft; do not merge
  as a substitute for the Admin steps above.**
