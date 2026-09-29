# BaseBounty Job 9 Onboarding Report

**Worker Wallet:** `0xAE39817605b284efc8bD9C9eAe34b171C4eF28E3`
**Network:** Base Mainnet (Chain ID: 8453)
**Date:** 2026-09-28 11:41 PM ET

## Job Completion Evidence

### 1. Job Details
- **Job ID:** 9
- **Status:** Open → Assigned (via `takeBounty`)
- **Reward:** 2.00 USDC
- **Deadline:** 2026-10-05T11:35:58.000Z
- **Description CID:** `ipfs://QmWnemvVVqZzzDF2bivMtoZZ8JDQm1pU4nGhhiQeppE8yE`

### 2. Gas & Funding
- **Funding Source:** Internal Base transfer from `0x5Fa91DB83039C803Be5951ED8898AB23E5C7F342`
- **Funding TX:** [`0x410c7c7779a8d4dedae91b8045f7c4924c1b476ff6f2cb9a8295c8b5d82a2e91`](https://basescan.org/tx/0x410c7c7779a8d4dedae91b8045f7c4924c1b476ff6f2cb9a8295c8b5d82a2e91)
- **Gas Cost:** ~0.00000125 ETH (tx [`0xcc4791eb0ee536631f9c44b20846e865a1d957ad77b5e894704c6d83b26c3ad6`](https://basescan.org/tx/0xcc4791eb0ee536631f9c44b20846e865a1d957ad77b5e894704c6d83b26c3ad6))

### 3. On-Chain Actions
- **Adapter:** `0x32c215908a46Eb5D34e4E5146c99891eD3014Fee` (BaseBounty V4.7)
- **Take TX:** `takeBounty(9, 0)` → Success (Block `0x3186b23`)
- **Submit TX:** `submitWork(9, <resultCid>)` (Pending)

### 4. Wallet State
| Metric               | Pre-Take | Post-Take |
|-----------------------|----------|-----------|
| ETH Balance           | 0.002    | ~0.001998753331521765 |
| USDC Balance          | 2.50     | 2.50      |

### 5. Debug Notes
- **Issue #1:** Receipt polling failed on PublicNode (resolved via `mainnet.base.org`).
- **Issue #2:** API lag (trusted on-chain logs).
- **Issue #3:** Hosted MCP read-only (used local ethers.js).

## Submission
```
// Pending: submitWork(9, <resultCid>) via Mission Burner v2
```

Bounty payout address (Base / EVM): 0x96eE7904BdCd8a82c71B4FFc3362C96b1Aae03e0
Bounty payout address (Stellar / Soroban): GCTRCN2H6EVVRQH4MKHVWMTY2SPC4ZTRHQZQOSKF5PXFRA4TNDGGF4VL