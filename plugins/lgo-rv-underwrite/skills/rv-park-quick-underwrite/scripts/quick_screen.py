#!/usr/bin/env python3
"""LGO RV Park Quick Screen calculator.

Runs the full first-pass math chain: gross income -> NOI -> implied cap ->
repriced offer -> offer matrix (8/9/10% caps) with DSCR and cash-on-cash
under both seller-finance and bank/SBA lenses -> Decision Matrix scoring.

Example:
    python quick_screen.py --sites 80 --occupied 52 --rent 450 \
        --asking 1800000 --other-income-monthly 800
"""
import argparse
import json


def pmt(rate_annual, years, principal):
    """Monthly payment, standard amortization."""
    r = rate_annual / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)


def scenario(offer, noi, down_pct, rate, amort_years, interest_only=False):
    down = offer * down_pct
    loan = offer - down
    if interest_only:
        annual_ds = loan * rate
    else:
        annual_ds = pmt(rate, amort_years, loan) * 12
    cash_flow = noi - annual_ds
    return {
        "down_payment": round(down),
        "loan_amount": round(loan),
        "annual_debt_service": round(annual_ds),
        "annual_cash_flow": round(cash_flow),
        "dscr": round(noi / annual_ds, 2) if annual_ds else None,
        "coc_pct": round(cash_flow / down * 100, 1) if down else None,
    }


def main():
    p = argparse.ArgumentParser(description="LGO RV park quick screen")
    p.add_argument("--sites", type=int, required=True, help="Total sites/pads")
    p.add_argument("--occupied", type=int, required=True, help="Occupied/paying sites")
    p.add_argument("--rent", type=float, required=True, help="Avg monthly rent per occupied site")
    p.add_argument("--asking", type=float, required=True, help="Asking price")
    p.add_argument("--other-income-monthly", type=float, default=0, help="Laundry/storage/propane etc, monthly")
    p.add_argument("--expense-ratio", type=float, default=0.50, help="Operating expense ratio (default 0.50)")
    p.add_argument("--market-cap", type=float, default=0.09, help="Market cap rate for repricing (default 0.09)")
    p.add_argument("--electric-monthly", type=float, default=0, help="Monthly electric bill if included in rent (billback upside)")
    p.add_argument("--sf-down", type=float, default=0.20, help="Seller finance down payment pct (default 0.20)")
    p.add_argument("--sf-rate", type=float, default=0.04, help="Seller finance interest rate (default 0.04)")
    p.add_argument("--sf-amort", type=int, default=30, help="Seller finance amortization years (default 30)")
    p.add_argument("--sba-down", type=float, default=0.30, help="Bank/SBA down payment pct (default 0.30)")
    p.add_argument("--sba-rate", type=float, default=0.085, help="Bank/SBA interest rate (default 0.085)")
    p.add_argument("--sba-amort", type=int, default=25, help="Bank/SBA amortization years (default 25)")
    args = p.parse_args()

    occupancy = args.occupied / args.sites if args.sites else 0
    rental_income = args.occupied * args.rent * 12
    other_income = args.other_income_monthly * 12
    gross = rental_income + other_income
    noi = gross * (1 - args.expense_ratio)
    implied_cap = noi / args.asking if args.asking else 0
    repriced = noi / args.market_cap if args.market_cap else 0
    billback_upside = args.electric_monthly * 12 * 0.825

    offers = {}
    for cap in (0.08, 0.09, 0.10):
        offer = noi / cap
        offers[f"{int(cap*100)}pct_cap"] = {
            "offer_price": round(offer),
            "vs_asking_pct": round((offer / args.asking - 1) * 100, 1),
            "seller_finance": scenario(offer, noi, args.sf_down, args.sf_rate, args.sf_amort),
            "seller_finance_interest_only": scenario(offer, noi, args.sf_down, args.sf_rate, args.sf_amort, interest_only=True),
            "bank_sba": scenario(offer, noi, args.sba_down, args.sba_rate, args.sba_amort),
        }

    # Decision Matrix scored at asking (cap) and at the 9%-cap offer (DSCR/CoC, seller finance)
    sf_at_reprice = offers["9pct_cap"]["seller_finance"]
    matrix = {
        "cap_rate": {"actual_pct": round(implied_cap * 100, 2), "target": ">= 8%", "pass": implied_cap >= 0.08},
        "dscr_seller_finance_at_9cap": {"actual": sf_at_reprice["dscr"], "target": ">= 1.25", "pass": (sf_at_reprice["dscr"] or 0) >= 1.25},
        "coc_yr1_at_9cap": {"actual_pct": sf_at_reprice["coc_pct"], "target": ">= 15%", "pass": (sf_at_reprice["coc_pct"] or 0) >= 15},
        "occupancy": {"actual_pct": round(occupancy * 100, 1), "target": ">= 85%", "pass": occupancy >= 0.85},
    }

    print(json.dumps({
        "inputs": vars(args),
        "occupancy_pct": round(occupancy * 100, 1),
        "price_per_site": round(args.asking / args.sites) if args.sites else None,
        "gross_income_annual": round(gross),
        "noi": round(noi),
        "implied_cap_pct": round(implied_cap * 100, 2),
        "repriced_at_market_cap": round(repriced),
        "reprice_vs_asking_pct": round((repriced / args.asking - 1) * 100, 1),
        "billback_upside_annual": round(billback_upside),
        "offer_matrix": offers,
        "decision_matrix": matrix,
        "passes": sum(1 for v in matrix.values() if v["pass"]),
    }, indent=2))


if __name__ == "__main__":
    main()
