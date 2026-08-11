# LGO Tools — Public Marketplace

Free LGO REI tools for Claude, starting with the **RV Park Quick Underwrite** — the first-pass deal screen our deal finders run on every RV park, MHP, and campground lead before it goes up the chain.

Drop in a listing, an OM, or your notes from a seller call. The skill collects the ~10 quick-screen inputs (asks once for whatever's missing), runs the math with a bundled calculator, scores the LGO Decision Matrix (cap rate ≥ 8%, DSCR ≥ 1.25, CoC ≥ 15%, occupancy ≥ 85%), and hands you a one-page **LGO Deal Snapshot** with a verdict: PURSUE / PURSUE ON TERMS / GET MORE INFO / PASS.

This is a screen, not full underwriting — it tells you whether a deal is worth a deeper look, and a deal that fails at the asking price isn't automatically dead. Price problems can be solved with terms.

## Install

In Claude Code / Cowork:

```
/plugin marketplace add SherpaOS/lgo-tools-marketplace
/plugin install lgo-rv-underwrite@lgo-tools
```

Then just paste a park listing or your seller-call notes and ask "worth chasing?"

## Updates

```
/plugin marketplace update lgo-tools
```

When we ship improvements (and we will — this is v0.1), updating pulls them automatically.

## Found a deal that scores PURSUE?

Submit it to the LGO REI acquisitions team with your Deal Snapshot attached.

---

— LGO REI / Jamie White · https://s4o.ai
