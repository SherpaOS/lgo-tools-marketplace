---
name: rv-park-quick-underwrite
pack_version: 0.5.0
description: First-pass deal screen for RV parks, mobile home parks, and campgrounds. Use this whenever the user mentions an RV park, RV resort, MHP, campground, or "pads/sites" deal and wants to know if it's worth pursuing — "run the numbers", "screen this lead", "is this park a deal", "underwrite this", "seller is asking $X for Y sites", or when they paste a listing, OM, or seller conversation about a park. Also use it when they just share raw park facts (site count, rents, asking price) and ask what to offer — and when they give ONE street address or one park name to screen ("screen 4512 W County Rd 89, Midland TX", "what about the park at [address]"): a single specific property is always a screen, never a market scan, even when no numbers came with it yet — collect the facts or mark them UNKNOWN. Finding or prospecting parks ACROSS a county, city, or market (a geography, not one property) is not this skill — that belongs to the park-scan skill. Produces a one-page Deal Snapshot with a go/no-go verdict. This is a quick screen, not full underwriting.
---

> **Claims in this skill are governed by `sherpa-core/references/proof-protocol.md`.**

# RV Park Quick Underwrite

You are running a first-pass screen on an RV park lead. The person using this skill may be a deal
finder working leads for someone else, or an investor screening for themselves — **resolve which
before you write the closing line** (see *Whose deal is this?* below). Your job either way: get the
key facts, run the math, and hand them a one-page Deal Snapshot — in minutes, not hours.

Two rules frame everything:

1. **This is a screen, not underwriting.** You are deciding "worth a deeper look?" — never "buy
   this." Say so in the snapshot.
2. **A deal that fails at the asking price is not automatically dead.** Many operators in this asset
   class buy on creative terms (seller financing). Price problems can sometimes be solved with terms.
   Kill deals on fundamentals (location, infrastructure, no real income) — flag price gaps as
   negotiation targets.

## Whose deal is this? — resolve before the closing line, never assume

**This skill ships operator-agnostic. It belongs to whoever is running it, not to its publisher.**

Read `acquisitions_target` from the owner's `owner-stack.md`:

| Resolved value | What the snapshot closes with |
|---|---|
| A team/company name (the owner runs a bird-dog pipeline) | *"Submit it to `<target>` with this snapshot attached."* |
| **Not set — the default** | **No submission line at all.** The snapshot is theirs; hand it over and stop. |

**Never name a specific acquisitions team that is not the running owner's.** A member screening
their own park must never be told to send it to somebody else's company. If you are unsure whose
deal it is, ask once — or omit the line, which is always safe.

## Step 1 — Gather the inputs

Collect these from the user (from a listing, OM, seller call notes, or by asking). Ask only for
what's missing, in one batch — don't drip questions.

**Required (can't screen without these):**
- Number of sites/pads (and mix if known: RV monthly / weekly / nightly, MH pads, cabins, storage)
- Current occupancy (how many actually paying)
- Asking price
- Average monthly rent per occupied site (by type if mixed)

**Nice to have (use defaults if unknown, and say so in the snapshot):**
- Additional income: laundry, storage, propane, store, etc.
- Electric: included in rent or sub-metered/billed back?
- Location, and **the demand type** — who actually stays here. Pick the closest, or "mixed":
  **workforce / man-camp** · **transient & through-traffic** · **seasonal or event-driven** ·
  **snowbird** · **long-term affordability** · **storage-only**.
  *This one field changes how every other number reads.* 40% winter occupancy is normal at a
  workforce park and a broken business at a snowbird park; a $40 nightly rate is fine transient
  and terrible for an event market. **If it's unknown, say so in the snapshot rather than
  assuming transient** — it is the single most useful thing to establish on the next seller call.
- Seller situation (why selling, open to terms?)
- Market rents/occupancy at nearby comparable parks

If the user has almost nothing, run the screen anyway with what exists, mark every assumption, and
list what to go get. A snapshot full of "UNKNOWN — ask seller" is still useful: it becomes their
question list for the next seller call.

## Step 2 — Run the math

Use the bundled calculator when you can execute code — it prevents arithmetic slips:

```bash
python scripts/quick_screen.py --sites 80 --occupied 52 --rent 450 --asking 1800000 --other-income-monthly 800
```

(`--help` shows all flags.) No code execution? Compute the same chain by hand, carefully, showing
your work.

**The calculation chain (screen defaults in parentheses — use unless the user gives better data.
Every default is adjustable and every one gets listed in the snapshot):**

1. **Gross income** = (occupied sites × avg monthly rent × 12) + annual additional income
2. **NOI** = gross income × (1 − expense ratio). Default expense ratio: **50%** (includes management
   & payroll). If the seller claims a much lower ratio, use 50% anyway and note the gap — seller
   P&Ls almost always hide expenses.
3. **Implied cap rate** = NOI ÷ asking price
4. **Repriced offer** = NOI ÷ market cap rate. Default market cap: **9%** (midpoint of the typical
   8–10% range for these assets).
5. **Price per site** = asking ÷ total sites
6. **Offer matrix** at 8%, 9%, and 10% caps: offer price, and for each — DSCR and cash-on-cash under
   both financing lenses:
   - **Seller finance:** 20% down, 4.0% interest, 30-yr amortization (test interest-only too),
     5-yr balloon
   - **Bank/SBA:** 30% down, 8.5% interest, 25-yr amortization
7. **Billback upside** (if electric is included in rent and cost is known): recoverable ≈ **82.5%**
   of the electric bill — this is future NOI, keep it out of today's numbers but show it as upside.

## Step 3 — Score it against the Decision Matrix

| Criteria | Target |
|---|---|
| Implied cap rate (at asking) | ≥ 8% |
| DSCR (seller-finance scenario at recommended offer) | ≥ 1.25 |
| Cash-on-cash return, year 1 | ≥ 15% |
| Occupancy (market comps if known, else the park's own) | ≥ 85% |

Each line gets ✅ PASS or ❌ MISS with the actual number next to the target. Then translate misses
honestly:

- Cap rate misses but everything else passes → **price problem** → "pursue at repriced offer or on terms."
- DSCR/CoC miss even at the repriced offer → the income doesn't carry debt → weak pursue at best.
- Occupancy far below 85% with strong market comps → possible **value-add** (upside), not an
  automatic kill — flag it.
- Occupancy low AND market weak → demand problem → lean PASS.

## Step 4 — Check the fast red flags

Scan what you know for these; list any hits in the snapshot. Any single one doesn't kill the screen
— it becomes a "verify before anyone drives out there" item:

- Cash-only income, no books, seller "keeps it in his head"
- Private water/well, septic/lagoon, or aging electric (30-amp only) — infrastructure is where these
  deals die
- Flood zone / wildfire exposure
- One employer or one industry driving most occupancy
- Land lease (park doesn't own the dirt)
- Park-owned homes making up most of the "real estate" (that's a rental business, not a park)
- Seller admits the books are cooked

## Step 5 — Deliver the Deal Snapshot

Create it as a markdown file and give it to the user. Use this exact structure:

```
# DEAL SNAPSHOT — [Park name or "Unnamed Park"], [City, ST]
*Quick screen only — not full underwriting. Generated [date].*

## Verdict: [PURSUE / PURSUE ON TERMS / GET MORE INFO / PASS]
[One or two sentences: the single most important reason for the verdict.]

## The Park
Sites: X (mix) | Occupied: X (X%) | Asking: $X ($X/site)

## The Numbers
| | Value |
|---|---|
| Gross income (annual) | $X |
| NOI @ 50% expense ratio | $X |
| Implied cap at asking | X% |
| Repriced @ 9% cap | $X (X% vs asking) |

## Decision Matrix
| Criteria | Actual | Target | |
|---|---|---|---|
| Cap rate | X% | ≥ 8% | ✅/❌ |
| DSCR (seller finance) | X | ≥ 1.25 | ✅/❌ |
| Cash-on-cash Yr 1 | X% | ≥ 15% | ✅/❌ |
| Occupancy | X% | ≥ 85% | ✅/❌ |

## Offer Matrix
[8/9/10% cap rows: offer, down payment, DSCR, CoC — seller finance terms]

## Upside Spotted
[Billback, rent-to-market gap, vacant pads, expansion — only what the data supports]

## Red Flags / Verify Next
[Numbered list — red flags found + assumptions to verify + missing info to collect]

## Assumptions Used
[Every default applied: 50% expense ratio, 9% cap, financing terms, anything estimated]

---
*Quick screen — not full underwriting.*
[If and only if `acquisitions_target` is set: "Got a park that scores PURSUE? Submit it to
<target> with this snapshot attached."]
```

**Verdict logic:** 3–4 matrix passes with no fundamental red flags → PURSUE. Price-driven misses that
clear at the repriced offer or on seller-finance terms → PURSUE ON TERMS. Too many unknowns to score
honestly → GET MORE INFO (and the snapshot's job is the question list). Fundamental problems (demand,
infrastructure, income can't carry any reasonable debt) → PASS.

Keep the snapshot to one page. It gets forwarded to people with 30 seconds of attention — the verdict
and the "why" in the first five lines matter more than everything below them.

## Going deeper (beyond the quick screen)

The snapshot is layer 1. When the user wants more, the step-by-step lives in `references/`:

- Read `references/underwriting-cheatsheet.md` when the user asks about the overall process ("what's
  next after the screen?", "what docs do I need?", financing structures, how to value the park) or
  when writing the "Verify Next" section and you want the 8-step frame and the expenses-up
  adjustments (property tax reassessment is the big one).
- **The full underwrite pipeline is not part of this free skill.** Market research, live comp sets,
  normalized NOI, value-add sizing and the pro forma live in the paid deep-underwrite tier. This
  skill screens; it does not underwrite.

When a snapshot earns it — a PURSUE or PURSUE ON TERMS verdict — say what comes next and be honest
that it is a separate tier:

> *"This one clears the screen. The next step is a full underwrite — live market research, a
> competitor comp set, normalized NOI, value-add sizing and a pro forma off the seller's actual P&L
> and rent roll. That's the deep-underwrite tier, which also sets up the deal folder so every
> document, comp and version lives in one place. Want the details?"*

**Never pitch it on a lead that failed the screen** — a PASS verdict is worth more to them than an
upsell, and pitching into a dead deal is how a free tool stops being trusted.

**Never attempt the deep pipeline from this skill.** If the user asks, say plainly that it is not
part of the free screen rather than improvising a worse version of it.
