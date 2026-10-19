# NRI SIP & Allocation Assistant — Phased Plan

*Drafted 2026-09-27. Extends the withdrawal planner into a general-purpose
accumulation + decumulation assistant for an Ireland-resident NRI.*

---

## ★ Source of truth (updated 2026-10-20)

**North star:** grow household wealth in **EUR, after Irish + Indian tax**, through a
steady monthly SIP. Short-term cash needs are kept out of market risk. The Indian
portfolio is wound down gradually and moved to EUR in a tax-efficient way. The app's
job is to tell us each month what to do, and why.

### Current plan

| Track | Plan | Status / next action |
|---|---|---|
| **Monthly SIP** | **Allocation v2** (below): €1,000/mo, Yash €500 + Sanskriti €500 | Not yet started → set up T212, Zerodha baskets, quarterly Revolut top-ups |
| **€7,500 lump sum** | **Allocation v2**, full growth. The Mar/Apr and Jul/Aug 2027 needs are now covered by the emergency fund. Deploy in 3 tranches, Oct–Dec 2026 | Not yet started |
| **Emergency fund** | ≈ 6 months of joint expenses, T212 cash | ✅ Done (2026-10) |
| **Pension / AVC** | Irish Life Empower (employer scheme). €2,500 single-premium AVC paid 28 Sep 2026, separate from the €7,500 pot | ✅ Claimed via Revenue (tax credits) |
| **Indian withdrawals** | FY25-26 / FY26-27 tranche plan (HSBC exit, ICICI trim, PP tranches) | ✅ Done. Closed out |

### Holdings snapshot (2026-10-20)

| Holding | Type | Ccy | Platform | Value |
|---|---|---|---|---|
| ICICI Prudential Large Cap Fund | Equity MF | INR | Kuvera | ₹1.36L |
| Nippon India ETF Nifty 50 BeES | ETF | INR | Zerodha / Kite | ₹47k |
| Nippon India ETF Nifty Next 50 Junior BeES | ETF | INR | Zerodha / Kite | ₹12k |
| Irish Life Empower (employee, employer, AVC) | Pension | EUR | Irish Life | — |

### Platforms (confirmed)

- **INR:** Kuvera (mutual funds), Zerodha / Kite / smallcase (ETFs, shares), HDFC NRE/NRO.
- **EUR:** Trading 212 (primary), Revolut (only where T212 can't: direct bonds, gold).
- **EU UCITS ETFs are excluded** (38% exit tax + 8-year deemed disposal). Global index
  exposure comes from the pension AVCs and INR ETFs instead.

### Decisions still open (in priority order)

1. ~~Irish tax on Indian funds vs shares~~ **Answered by desk research**
   ([research_irish_tax_inr_vehicles.md](research_irish_tax_inr_vehicles.md)).
   Indian MFs/ETFs ≈ 52% Irish income tax, no loss relief. Indian direct shares at 31%
   CGT. Result: new INR money goes to direct-share baskets only.
2. **Compliance check (urgent):** existing Indian MF/ETF holdings and any 2025 Indian
   fund disposals likely make you a chargeable person, so you need a **Form 11**, not
   just the myAccount return. 2025 deadline: 31 Oct 2026, or mid-Nov if filed *and*
   paid on ROS.
3. **Domicile before naturalisation:** a one-off written opinion (async, by email) on
   whether you are non-domiciled today, and whether to reset Indian MF/ETF gains before
   naturalising.
4. **AVC vs liquid EUR equity:** AVCs get 40% relief and tax-free growth, and you have
   large headroom under the 20% limit. Decide how much of the SIP to lock until
   retirement.
5. **1 Jul 2027 review:** the Savings & Investment Account (€12k/yr each, tax-free
   inside, 1% levy above €50k) may make EU ETFs the best liquid vehicle.

### What we'd have wanted to know on day 1 (intake checklist)

Each of these, learned late, sent us back to redo earlier work:

| Fact learned late | What it would have saved |
|---|---|
| Irish tax resident, **soon to naturalise** (domicile) | The first tax engine was India-LTCG-only. Irish tax on Indian funds may outweigh Indian LTCG, so the whole INR-vs-EUR split depends on it |
| **Existing employer pension with AVCs** (Irish Life) | The "should we add a PRSA?" question and part of the EUR equity sleeve. The best-relieved wrapper was already in place |
| **Household of two contributors** (Sanskriti) | A second recompute: per-person accounts, two CGT exemptions, spouse transfers |
| **Real budget (€1,000, not €1.5–2k)** and a surplus-cash buffer first | One full allocation pass |
| **Cash-need dates** (Mar/Apr €4k, Jul/Aug €3k) | A generic 12-month split that had to be redone |
| **Accounts actually held** (T212, Revolut, Kuvera, Zerodha/Kite/smallcase, HDFC NRE/NRO) | Researching platforms that turned out not to apply |
| **"Gold" meant price exposure via the apps**, not bars | The early bullion-spread discussion |
| **"Tax-efficient" claims must be tested in the residence country first** (Indian ETFs looked efficient in India, ~52% in Ireland) | Allocation v1/v1.1 sleeves that had to be swapped for direct shares |
| **Goal hierarchy**: accumulate in EUR (main), withdraw from India (secondary), short-term liquidity (constraint) | The app was built withdrawal-first, then extended. Building in this order would have shaped the data model (household ledger, both tax years) from the start |

Use this as the intake checklist for any future change: **residency/domicile, household,
existing wrappers, accounts, budget, dated cash needs, goal priority**.

## Goal

Each month, take a flexible budget (€1,500–2,000) and recommend how much goes into
each of five buckets, optimised for **after-tax wealth in EUR** under both Irish and
Indian tax rules. Heavy analysis (interventions, counterfactuals) runs offline. The
Streamlit app only reads the cached results.

| Bucket | Currency | Examples |
|---|---|---|
| Active mutual funds | INR | Parag Parikh Flexi Cap, ICICI Pru Large Cap (existing) |
| Index funds | INR | Nifty 50 / Next 50 index funds |
| Debt funds / bonds | EUR | short/intermediate euro govt bond funds, direct bonds |
| Stocks | EUR | direct EU/US shares via an EU broker |
| ETFs | EUR | UCITS world/Europe equity ETFs |

**Debt/equity rule:** debt % = age. At 31 that is 31% debt / 69% equity, and the debt
share rises 1 pp per year (glide path). This applies to the long-term portfolio only.
Short-term reserves (e.g. the €7,500 12-month pot) are tracked separately and excluded.

## Design principles

1. **One unit of account: EUR after tax.** Every return, forecast and recommendation
   is expressed in EUR net of Indian tax, Irish tax, foreign-tax credit, FX and
   remittance costs.
2. **Rebalance with new money, not sales.** Rebalancing is done by steering monthly
   contributions, so no disposal happens in either jurisdiction. Recommending a sale
   is opt-in only.
3. **Tax rules are versioned config, not code.** Every rate cites its source and has a
   `verified_on` date. The app warns when a rule is more than 12 months old.
4. **Offline inference, online reading.** MCMC and causal jobs write parquet under
   `portfolio_app/.cache/`, and the app loads it. This extends the existing
   `data_sources.py` cache pattern.
5. **Log every recommendation, then score it.** This is what lets the system improve
   itself (Phase 5).

---

## Phase 0 — Tax, currency and ledger foundations *(blocker)*

**Why it comes first:** the Irish tax treatment of Indian mutual funds may outweigh
everything else. If Indian MF gains are taxed in Ireland as income at the marginal
rate, the INR buckets become much less attractive, and the whole allocation changes.

- `tax_rules/ireland.yaml`, `tax_rules/india.yaml`: rates, exemptions, sources, `verified_on`.
  - **Ireland** (tax year = **calendar year**):
    - CGT 31% from 7 Oct 2026 (was 33%), €1,270 annual exemption, losses can be offset
      and transferred between spouses.
    - EU/EEA UCITS ETFs and funds: exit tax 38% in 2026, 35% from 1 Jan 2027, 8-year
      deemed disposal, no loss offset.
    - Non-EU/EEA/OECD funds (Indian MFs **and** NSE ETFs): Case IV income at the
      marginal rate + USC + PRSI (~52%), no loss relief, no 8-year deemed disposal.
    - DIRT 33% on deposit interest.
    - Irish government bond gains are CGT-exempt (s.607 TCA). Coupons are taxed at
      the marginal rate plus USC and PRSI.
    - **Indian MFs:** India is not an EU/EEA/OECD country, so the offshore-fund rules
      likely tax gains as income at the marginal rate. *Confirm with an adviser.*
    - **Remittance basis:** if you are Irish-resident but not Irish-domiciled, foreign
      gains may only be taxed when remitted to Ireland. This interacts directly with
      the repatriation plan. *Confirm.*
    - Gold ETC classification (CGT vs exit tax) is disputed. *Confirm.*
  - **India** (tax year = **April–March**):
    - Equity LTCG 12.5% above ₹1.25L on holdings over 12 months; STCG 20%.
    - Debt funds bought after April 2023 are taxed at slab rate regardless of holding
      period.
    - TDS is deducted on NRI redemptions.
    - The India–Ireland DTAA gives a foreign-tax credit.
- `tax_engine.py`: `after_tax_eur(lot, disposal_date, profile)` applies both regimes,
  the DTAA credit, and the FY mismatch (Irish Jan–Dec vs Indian Apr–Mar). The existing
  `portfolio.py` LTCG functions become the India leg.
- `fx.py`: EUR/INR history (ECB reference rate, falling back to `EURINR=X`) and a
  remittance cost model (FX spread + fixed fee per transfer).
- **Lot-level ledger** (`holdings.parquet`: date, units, price, currency, bucket,
  broker). FIFO tax and deemed-disposal tracking need lot-level data. This replaces the
  current invested/current_value totals in `FundHolding`.
- `profile.yaml`: age, residency, domicile, Irish marginal rate, brokers used.

**Done when:** the engine passes the existing `tests/test_portfolio.py` India cases and
hand-worked Irish cases for each asset type, and the open questions below are answered
or explicitly assumed.

## Phase 1 — Descriptive analytics *(Pearl rung 1: association)*

This is the toolkit from the index-investing video, in EUR terms.

- **Rolling returns** (1/3/5/7/10 yr): min, median and max per fund and index, in both
  INR and EUR.
- **Drawdowns**: underwater curve, max drawdown, time to recovery.
- **Core-satellite backtester**: first reproduce the linked sheet (`Core-Satellite
  Portfolio Scenarios.xlsx`), then fix its weak spots:
  - TRI instead of price indices
  - real gold (in EUR) instead of a fixed 1.09% per month
  - a real debt proxy instead of a fixed 0.61% per month
  - EUR conversion
  - reported as XIRR plus drawdown
- **Overlap**: top-N holding overlap matrix and top-5 concentration. MVP input is an
  uploaded AMC factsheet CSV, because mfapi.in only has NAVs.
- **Cost drag**: TER + tracking difference over the horizon (TER entered by hand).
- New tickers in `data_sources.py`: EUR ETF proxies, euro govt bond index, gold in EUR,
  Nifty TRI where available.

**Done when:** fed the sheet's own assumptions, the backtester matches its 11.23% /
13.29% within ~0.3 pp. The corrected results are then shown alongside.

## Phase 2 — Monthly SIP allocator *(forward-looking)*

- Extend `factor_model.py` to model EUR assets and **EUR/INR jointly** with Indian
  equity. INR tends to weaken during global risk-off, which is exactly when Nifty
  falls, so the two must be modelled together rather than separately.
- **Optimiser** (scenario-based over posterior draws, `scipy.optimize`):
  - choose contributions `c_i ≥ 0` with `Σ c_i = B`, where B is between €1,500 and €2,000
  - minimise drift from the target weights (age rule plus user caps) − utility
  - utility = `(1-λ)·E[W] + λ·CVaR₁₀[W]`, where W = after-tax EUR wealth. λ is the same
    risk-aversion input the withdrawal planner uses.
  - constraints:
    - at most 2–3 funds per bucket (overlap lesson)
    - overlap cap
    - minimum trade size (broker fees)
    - INR remittances batched (monthly vs quarterly, whichever is cheaper after FX
      fees)
- **Output:** "This month: €X → A, €Y → B …", with a one-line reason per bucket and a
  drift-vs-target chart.
- Every recommendation is logged (inputs, model version, posterior hash) to
  `logs/recommendations.jsonl`.

**Done when:** the recommendation always sums to B, never proposes a sale by default,
and is deterministic for a fixed seed.

## Phase 3 — Structural causal model and interventions *(rung 2: the do-operator)*

- **DAG:**
  - global risk (VIX, US yields) → foreign-investor (FII) flow proxy → EUR/INR, Nifty
  - ECB rate → EUR bonds, EUR/INR
  - oil → INR, Indian inflation
  - policy nodes (allocation, SIP amount, rebalance rule, remittance timing) →
    after-tax EUR wealth
- Implemented in PyMC with `pm.do` / `pm.observe` (pymc-modeling skill).
- **Queries:**
  - `do(EURINR +10%)`
  - `do(ECB +100bp)`
  - `do(pause SIP when drawdown > 20%)`
  - `do(debt share ∈ {25, 31, 40}%)`
- **Where the do-operator earns its keep:** your allocation doesn't move markets, so
  `do(allocation)` reduces to plain simulation. The value is on the market-shock nodes.
  Weak INR co-occurs with risk-off, so *conditioning* on a weak rupee overstates equity
  losses compared with *intervening* on the rupee alone.
- Offline job: `jobs/run_interventions.py` → `.cache/causal/*.parquet`. The app gets a
  "What-if" tab that reads them.
- **Validation:** check the DAG's implied conditional independences against data, plus
  prior and posterior predictive checks.

## Phase 4 — Counterfactuals *(rung 3)*

- Abduction–action–prediction: infer the exogenous shocks from realised history, then
  replay them under alternative policies.
- **Backward questions:**
  - "SIP from Jan 2020 vs lump sum"
  - "had I paused SIPs in Mar 2020"
  - "had I held 31% debt"
  - "monthly vs quarterly remittance"
  - regret distributions for each
- **Forward:** every logged Phase 2 recommendation is re-scored against the
  alternatives once its outcome is realised.
- Offline monthly job: `jobs/run_counterfactuals.py`.

## Phase 5 — Self-improvement loop and integration

- **Scoring:**
  - forecast calibration (P10–P90 coverage, CRPS)
  - recommendation regret from Phase 4
  - failures logged to `logs/failures.jsonl`: fetch errors, divergences, r̂ > 1.01,
    calibration misses
- **Automatic responses:**
  - widen priors / retune block size when coverage drifts
  - flag stale tax rules
  - surface repeated failure types in the app
- **Integration with the withdrawal planner:**
  - one ledger for both accumulation and decumulation
  - FY-aware on both calendars
  - Indian LTCG harvesting (sell and rebuy to use ₹1.25L) is only recommended if it
    doesn't trigger a larger Irish tax bill

---

## Open questions (for you or a tax adviser)

1. Irish domicile status. Does the remittance basis apply?
2. ~~Irish marginal rate~~ **Likely 40%:** 2025 payroll pension contributions imply a salary
   above the 40% band. Confirm from the 2025 Statement of Liability.
3. Irish tax treatment of Indian MFs: offshore-fund regime, rate, loss relief.
4. Gold ETC classification: CGT or exit tax.
5. ~~Should a **PRSA/pension** be a 6th bucket?~~ **Superseded:** an employer scheme with AVCs
   already exists (Irish Life Empower), so the question becomes AVC vs taxable equity (see Source of truth).
   Original note: At 30–39, contributions up to 20% of
   earnings get income-tax relief at the marginal rate. For long-term EUR equity this
   likely beats every other wrapper, at the cost of locking the money until retirement.
6. ~~Which EU broker(s)?~~ **Answered:** Trading 212 (commission-free EUR stocks and
   ETFs, auto-invest "Pies" for the monthly EUR SIP, interest on cash) and Revolut
   Trading (EEA government/corporate bonds, €100 min, 0.25% fee; commodities at
   0.49–0.99% per order depending on plan). Neither broker withholds Irish CGT or exit
   tax, so the tax engine must produce a self-assessment summary (Form 11/12).

## Recommended first slice

**Phase 0 plus the Phase 1 backtester.** Phase 0 settles whether the INR buckets make
sense after Irish tax. The backtester needs no new modelling and reuses the existing
`data_sources.py` fetchers.

---

## Target allocation v1 *(superseded by v2)*

*Agreed 2026-10-03. Age 31 → 31% defensive / 69% equity. Percentages are of each
monthly SIP (€1,500–2,000), so the amounts scale with the budget. When the budget
changes from month to month, the extra or shortfall goes to whichever bucket is most
underweight, rather than being spread pro-rata.*

| # | Sleeve | E/D | Instrument | Ccy | Platform | % | Irish tax | Indian tax | Condition |
|---|---|---|---|---|---|---|---|---|---|
| 1 | EUR govt bonds | D | Euro govt bond UCITS ETF, or direct EUR govt bonds bought quarterly | EUR | T212 Pie / Revolut Bonds | 26 | ETF: 38% exit + 8-yr deemed disposal. Irish govt bond gains are CGT-exempt | — | Prefer direct Irish govt bonds when a suitable maturity is listed |
| 2 | Gold | D (defensive) | Gold, bought quarterly | EUR (USD-priced) | Revolut Commodities | 5 | CGT 33%, €1,270 exemption | — | — |
| 3 | Global equity core | E | Accumulating world UCITS ETF | EUR | T212 Pie | 34 | 38% exit + 8-yr deemed disposal | — | Shrinks if a PRSA is adopted |
| 4 | EUR stocks satellite | E | 5–8 direct shares | EUR | T212 | 10 | CGT 33%, losses offset, €1,270 exemption | — | — |
| 5 | India large-cap core | E | Nifty 50 index MF **or** stock-only large-cap smallcase | INR | Zerodha (Coin / smallcase, NRE-PIS) | 15 | MF: likely offshore-fund income tax. Shares: CGT 33% | LTCG 12.5% > ₹1.25L, STCG 20% | Vehicle decided by the Phase 0 Irish-tax answer |
| 6 | India flexi-cap | E | Parag Parikh Flexi Cap SIP | INR | Scripbox | 10 | Likely offshore-fund income tax | LTCG 12.5% > ₹1.25L | — |
| 7 | ICICI Pru Large Cap | E | Hold; no new money | INR | Scripbox | 0 | — | — | Overlaps sleeve 5; remains the withdrawal source |
| 8 | Pension (PRSA) | E | Global equity PRSA | EUR | TBD | 0 → TBD | Contributions get relief at the marginal rate | — | If adopted, funded first from sleeve 3 |

INR sleeves (5 + 6 = 25%) are remitted to NRE **quarterly** to reduce FX and transfer fees.

### v1.1 — starting budget €1,000/month, two contributors (2026-10-03) *(superseded by v2)*

Same percentages as v1, at €1,000/month: Yash €500 + Sanskriti €500. INR sleeves stay
in Yash's name (existing NRE/Scripbox/Zerodha accounts). Each spouse holds some
CGT-taxed assets (stocks, gold) so that both €1,270 annual CGT exemptions get used.
Transfers between spouses are CGT-free.

| # | Sleeve | Yash | Sanskriti | Total |
|---|---|---|---|---|
| 1 | EUR govt bonds | €130 | €130 | €260 |
| 2 | Gold (quarterly) | €25 | €25 | €50 |
| 3 | Global equity ETF | €45 | €295 | €340 |
| 4 | EUR stocks | €50 | €50 | €100 |
| 5 | India large-cap core | €150 | — | €150 |
| 6 | Parag Parikh Flexi Cap | €100 | — | €100 |
| | **Total** | **€500** | **€500** | **€1,000** |

**Open question 1 update:** Irish naturalisation is strong evidence of an Irish domicile
of choice. Plan on the assumption that **no remittance basis** applies (worldwide gains
taxed as they arise). The ledger and profile need a `household` level with
per-person accounts and per-person CGT exemptions.

---

## Target allocation v2 (2026-10-20): current

**Principle** (by volatility; age 31):

| Bucket | Rule | % |
|---|---|---|
| Low | 10% fixed | 10 |
| Medium | (age − 10)% | 21 |
| High | (100 − age)% | 69 |

**Changes from v1.1:**
- No EU UCITS ETFs (exit tax).
- No new Indian MFs or ETFs (~52% Irish tax). The user's preferred INR vehicles are
  swapped for Zerodha direct-share baskets with the same exposure.
- INR is held at ~20% as a deliberate diversifier.

| # | Bucket | Sleeve | Ccy | Platform | Owner | % | €/mo SIP | € lump sum | Irish tax | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Low | EUR govt bonds (Irish where listed, 2–5 yr) | EUR | Revolut Bonds | Both | 5 | 50 | 375 | Irish govt: gain CGT-free, coupon income. Others: CGT 31% | SIP: hold in T212 cash, buy quarterly (€150) |
| 2 | Low | Gold price exposure | EUR (USD-priced) | Revolut Commodities | Both | 5 | 50 | 375 | CGT 31%, €1,270 each | Quarterly. Avoid T212 gold ETCs until their classification is checked |
| 3 | Medium | Global generalist investment trusts (e.g. F&C, Alliance Witan) | GBP | T212 | Both | 11 | 110 | 825 | Likely CGT 31% (unresolved) | Check each ticker is buyable on T212 EU (KID) |
| 4 | Medium | INR large-cap basket (top Nifty 50 names) replacing new Nifty/Next 50 ETF buys | INR | Zerodha smallcase / Kite | Yash | 10 | 100 | 750 | CGT 31%, Indian LTCG credited | Remit quarterly (~₹32k) |
| 5 | High | EUR/US direct stocks, 15–25 names over time | EUR/USD | T212 | Both | 59 | 590 | 4,425 | CGT 31%, losses usable | Sector tilt below |
| 6 | High | INR mid/small/micro basket (60/30/10) | INR | Zerodha smallcase / Kite | Yash | 10 | 100 | 750 | CGT 31% | Remit quarterly with row 4 |
| | | **Total** | 80% EUR / 20% INR | | | **100** | **1,000** | **7,500** | | |

**SIP by person:**
- **Yash €500:** rows 1+2 €50, row 3 €55, rows 4+6 €200, row 5 €195.
- **Sanskriti €500:** rows 1+2 €50, row 3 €55, row 5 €395.

**Lump sum:**
- Yash's money.
- Gift up to half of rows 1–3 and 5 to Sanskriti (spouse transfers are CGT-free) so
  that both €1,270 CGT exemptions get used.
- Deploy in thirds: Oct, Nov and Dec 2026.

**Existing holdings** (ICICI Large Cap MF, Nifty BeES, Junior BeES):
- Hold, and put no new money in.
- Selling them triggers ~52% Irish tax on the gain.
- Declare them on Form 11.

**Diversification targets** (liquid equity, rows 3–6):
- **Market cap:** large ≈ 65%, mid ≈ 20%, small ≈ 12%, micro ≤ 3%.
- **Sectors:** INR baskets are ~30–35% financial services. Row 5 offsets this by
  underweighting financials (≤ 10%) and spreading across:
  - industrials
  - healthcare
  - technology
  - consumer cyclical/defensive
  - basic materials
  - energy/utilities

  Target: no single sector above 25% of liquid equity.
- The Phase 2 allocator will optimise these splits from posterior draws. Until then,
  they are fixed guide rails.
