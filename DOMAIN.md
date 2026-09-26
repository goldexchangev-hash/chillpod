# Connecting `ichillpod.com` to the Render static site

The product domain is **`ichillpod.com`** (not `chillpod.com` — we do not own that).
`www.ichillpod.com` should redirect to the root domain.

Getting the domain live takes three parts. `render.yaml` only covers the first.

| Part | Where | Done by |
| --- | --- | --- |
| 1. Declare the domains on the service | `render.yaml` (`domains:`) or Render Dashboard | this repo / you |
| 2. Point DNS at Render | GoDaddy DNS | you (manual) |
| 3. Verify the domain so Render issues TLS | Render Dashboard | you (manual) |

## 1. Declare the domains on the Render service

`render.yaml` already lists both domains:

```yaml
    domains:
      - ichillpod.com
      - www.ichillpod.com
```

- **If the `chillpod` service was created from this Blueprint** (Render → New → Blueprint), a
  Blueprint sync on the connected branch (`main`) adds both domains to the service automatically.
  Check Render → Blueprints → *chillpod* for the sync result.
- **If the service was created manually** (New → Static Site, not via Blueprint), `render.yaml`
  is ignored. Add the domain by hand instead: open the service → **Settings** → **Custom Domains**
  → **+ Add Custom Domain** → enter `ichillpod.com` → **Save**. Render auto-adds
  `www.ichillpod.com` with a redirect to the root domain.

Either way, the Dashboard will now list both domains with a *DNS update needed* status.
While you're there, copy two values you need for step 2:

- the service's **`onrender.com` hostname** (shown at the top of the service page — expected
  to be `chillpod.onrender.com`, but Render may append a suffix if the name was taken), and
- the **A-record IP** Render shows next to the root domain (currently `216.24.57.1`).

## 2. GoDaddy DNS records

GoDaddy does not support ALIAS/ANAME records or CNAME flattening, so the apex domain must use
an **A record** and `www` uses a **CNAME**.

GoDaddy → **My Products** → `ichillpod.com` → **DNS** → **DNS Records**.

### 2a. Remove what is there now

The domain currently points at GoDaddy's forwarding service, which is what produces the
`308` redirect and the failed TLS handshake:

- **Delete** the two `A` records for `@` pointing to `76.223.105.230` and `13.248.243.5`.
- **Delete** the `CNAME` record `www` → `ichillpod.com` (it will be replaced below).
- Under the **Forwarding** section of the DNS page, **remove any Domain Forwarding** entry for
  `ichillpod.com`. Forwarding re-creates the parking A records, so DNS changes will not stick
  until it is off.
- Delete any `AAAA` records if present (there are none today). Render is IPv4-only and stale
  `AAAA` records break the site for some clients.

### 2b. Add the Render records

| Type | Name | Value | TTL |
| --- | --- | --- | --- |
| `A` | `@` | `216.24.57.1` (confirm against the IP shown in the Render Dashboard) | 600 s (or the lowest allowed) |
| `CNAME` | `www` | `chillpod.onrender.com` (use the exact hostname from the Dashboard) | 600 s |

Leave the `NS` records (`ns39.domaincontrol.com` / `ns40.domaincontrol.com`) and any
`MX`/`TXT` records for email alone. The domain has no `CAA` records, so nothing to add there;
if you ever add CAA records, include `letsencrypt.org` and `pki.goog`.

## 3. Verify in Render

1. Wait a few minutes for DNS to propagate. Check with:

   ```bash
   dig +short ichillpod.com A        # expect 216.24.57.1 only
   dig +short www.ichillpod.com CNAME # expect chillpod.onrender.com.
   ```

   Optionally flush public resolver caches (Google Public DNS, Cloudflare 1.1.1.1) to speed it up.
2. In Render → service → **Settings** → **Custom Domains**, click **Verify** next to each domain.
3. On success Render issues the TLS certificate automatically (a few minutes). A `502` right after
   verification means routing is still updating — wait and retry.
4. Confirm: `https://ichillpod.com` serves the site and `https://www.ichillpod.com` redirects to it.

## Optional: turn off the `onrender.com` URL

Once the custom domain works you can hide the default `chillpod.onrender.com` URL, either in
**Settings → Custom Domains → Render Subdomain → Disabled**, or by adding
`renderSubdomainPolicy: disabled` to the service in `render.yaml`.

## Email

The site's fallback pre-order link is `hello@ichillpod.com`. That mailbox does not exist until
you create it — the easiest option is GoDaddy → `ichillpod.com` → **Email Forwarding**, forwarding
`hello@ichillpod.com` to an inbox you already use.

References: [Render custom domains](https://render.com/docs/custom-domains),
[Render DNS for other providers](https://render.com/docs/configure-other-dns),
[Blueprint `domains` field](https://render.com/docs/blueprint-spec#domains).
