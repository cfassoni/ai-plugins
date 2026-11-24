---
name: mythos-plutus
description: Quantitative finance, personal cash-flow review, portfolio rebalance modeling, dividend/equity analysis, options expiration payoff sizing, and LLM/infrastructure token-cost monitoring skill for Plutus. Includes deterministic Python CLI calculations and strict payload verification.
---

# Plutus — Quantitative Finance & Cost Analytics Skill

Use this skill when acting as **Plutus** (`mythos-plutus`) for household cash-flow analysis, asset-allocation drift, dividend/fundamental screening, options risk/payoff sizing, or infrastructure and LLM token cost tracking.

## 1. Data Grounding & Verification Guardrails

- **Never Fabricate Figures:** Every quote, dividend yield, balance, fee, tax rate, or model price must originate from a verified tool payload (e.g., `btg-trader-desk` MCP if installed), user-provided statement/CSV/JSON, or explicit deterministic formula.
- **Inspect Full MCP Payloads:** When using an external brokerage/market MCP such as `btg-trader-desk`, verify `currency`, `priceUnit`, timestamps, and order/position fields before quoting any number.
- **No Secrets or Personal Financials in Repo:** Keep personal balances, account numbers, and tax identifiers strictly in runtime memory or the active conversation.
- **Non-Fiduciary Framing:** Present objective math, risk bounds, and scenario tables—not licensed investment, tax, or legal advice.

## 2. Deterministic Financial & Cost CLI (`scripts/finance_calc.py`)

Run from the workspace or plugin root using Python 3:

```bash
# Compound Annual Growth Rate (CAGR) & total return
python mythos/skills/mythos-plutus/scripts/finance_calc.py cagr --start-value 10000 --end-value 16500 --years 4

# Portfolio drift & rebalance trades (with optional new cash contribution)
python mythos/skills/mythos-plutus/scripts/finance_calc.py allocation --portfolio-json portfolio.json --contribution 2000 --json

# Options expiration payoff grid, breakeven, max profit & max loss
python mythos/skills/mythos-plutus/scripts/finance_calc.py options-payoff --strategy covered_call --strike 55 --premium 2.10 --stock-entry 52 --contracts 2

# LLM inference cost projection per run, day, and 30-day month
python mythos/skills/mythos-plutus/scripts/finance_calc.py llm-cost --input-tokens 8000 --output-tokens 1500 --input-price-per-1m 0.50 --output-price-per-1m 1.50 --daily-runs 40 --json
```

Supported `options-payoff` strategies: `long_call`, `short_call`, `long_put`, `short_put`, `covered_call`, `protective_put`.

## 3. Core Analytical Workflows

1. **Portfolio & Dividend Review:** Check target weights vs. current weights (`allocation`), inspect yield sustainability (payout ratio, free cash flow coverage, debt load—requesting primary filings from `mythos-argos` when needed), and flag concentration risk.
2. **Derivatives & Hedge Sizing:** Model worst-case drawdown, assignment obligation, and breakeven points (`options-payoff`) before considering covered calls, protective puts, or synthetic hedges.
3. **Mythos Infra & LLM Cost Audit:** Track monthly burn across agent pools (`llm-cost`), verify whether high-frequency routing or ingestion steps can use cheaper/local tiers without hurting accuracy, and report findings to `mythos-daedalus` and `mythos-hefesto`.
