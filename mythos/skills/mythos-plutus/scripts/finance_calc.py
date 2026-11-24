#!/usr/bin/env python3
"""Deterministic financial, portfolio allocation, options payoff, and LLM cost calculator for Mythos Plutus."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

STRATEGIES = (
    "long_call",
    "short_call",
    "long_put",
    "short_put",
    "covered_call",
    "protective_put",
)


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"Value must be > 0, got {value}")
    return parsed


def _non_negative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError(f"Value must be >= 0, got {value}")
    return parsed


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"Value must be > 0, got {value}")
    return parsed


def cmd_cagr(args: argparse.Namespace) -> dict[str, Any]:
    total_return = (args.end_value / args.start_value) - 1.0
    cagr = (args.end_value / args.start_value) ** (1.0 / args.years) - 1.0
    return {
        "start_value": round(args.start_value, 2),
        "end_value": round(args.end_value, 2),
        "years": round(args.years, 4),
        "total_return_pct": round(total_return * 100.0, 2),
        "cagr_pct": round(cagr * 100.0, 2),
    }


def cmd_allocation(args: argparse.Namespace) -> dict[str, Any]:
    raw = sys.stdin.read() if args.portfolio_json == "-" else Path(args.portfolio_json).read_text(encoding="utf-8")
    items = json.loads(raw)
    if not isinstance(items, list) or not items:
        raise ValueError("Portfolio JSON must be a non-empty array of {asset, value, target_pct}.")

    current_total = 0.0
    target_sum = 0.0
    parsed_items: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict) or "asset" not in item or "value" not in item or "target_pct" not in item:
            raise ValueError(f"Item #{idx} must include 'asset', 'value', and 'target_pct'.")
        value = float(item["value"])
        target_pct = float(item["target_pct"])
        if value < 0 or target_pct < 0:
            raise ValueError(f"Item #{idx} cannot have negative value or target_pct.")
        current_total += value
        target_sum += target_pct
        parsed_items.append({"asset": str(item["asset"]), "value": value, "target_pct": target_pct})

    if abs(target_sum - 100.0) > 0.05:
        raise ValueError(f"Target weights must sum to 100%, got {target_sum:.2f}%.")

    projected_total = current_total + args.contribution
    if projected_total <= 0:
        raise ValueError("Total portfolio value after contribution must be > 0.")

    rows = []
    for item in parsed_items:
        current_pct = (item["value"] / current_total * 100.0) if current_total > 0 else 0.0
        target_value = projected_total * (item["target_pct"] / 100.0)
        rebalance_delta = target_value - item["value"]
        rows.append({
            "asset": item["asset"],
            "current_value": round(item["value"], 2),
            "current_pct": round(current_pct, 2),
            "target_pct": round(item["target_pct"], 2),
            "drift_pct": round(current_pct - item["target_pct"], 2),
            "target_value": round(target_value, 2),
            "rebalance_delta": round(rebalance_delta, 2),
        })

    return {
        "current_total": round(current_total, 2),
        "contribution": round(args.contribution, 2),
        "projected_total": round(projected_total, 2),
        "positions": rows,
    }


def _payoff_at_spot(
    strategy: str,
    spot: float,
    strike: float,
    premium: float,
    stock_entry: float,
    scale: float,
) -> float:
    call_intrinsic = max(0.0, spot - strike)
    put_intrinsic = max(0.0, strike - spot)
    if strategy == "long_call":
        per_share = call_intrinsic - premium
    elif strategy == "short_call":
        per_share = premium - call_intrinsic
    elif strategy == "long_put":
        per_share = put_intrinsic - premium
    elif strategy == "short_put":
        per_share = premium - put_intrinsic
    elif strategy == "covered_call":
        per_share = (spot - stock_entry) + (premium - call_intrinsic)
    else:  # protective_put
        per_share = (spot - stock_entry) + (put_intrinsic - premium)
    return per_share * scale


def cmd_options_payoff(args: argparse.Namespace) -> dict[str, Any]:
    scale = args.contracts * args.multiplier
    stock_entry = args.stock_entry if args.stock_entry is not None else args.strike
    if args.strategy in ("covered_call", "protective_put") and args.stock_entry is None:
        raise ValueError(f"--stock-entry is required for strategy '{args.strategy}'.")

    spot_min = args.spot_min if args.spot_min is not None else max(0.0, round(args.strike * 0.7, 2))
    spot_max = args.spot_max if args.spot_max is not None else round(args.strike * 1.3, 2)
    if spot_max <= spot_min:
        raise ValueError("--spot-max must be greater than --spot-min.")

    step = (spot_max - spot_min) / args.steps
    grid = []
    for i in range(args.steps + 1):
        spot = spot_min + i * step
        pnl = _payoff_at_spot(args.strategy, spot, args.strike, args.premium, stock_entry, scale)
        grid.append({"spot": round(spot, 2), "pnl": round(pnl, 2)})

    if args.strategy == "long_call":
        breakeven = round(args.strike + args.premium, 2)
        max_profit: float | str = "Unlimited"
        max_loss: float | str = round(-args.premium * scale, 2)
    elif args.strategy == "short_call":
        breakeven = round(args.strike + args.premium, 2)
        max_profit = round(args.premium * scale, 2)
        max_loss = "Unlimited"
    elif args.strategy == "long_put":
        breakeven = round(max(0.0, args.strike - args.premium), 2)
        max_profit = round(max(0.0, args.strike - args.premium) * scale, 2)
        max_loss = round(-args.premium * scale, 2)
    elif args.strategy == "short_put":
        breakeven = round(max(0.0, args.strike - args.premium), 2)
        max_profit = round(args.premium * scale, 2)
        max_loss = round(-max(0.0, args.strike - args.premium) * scale, 2)
    elif args.strategy == "covered_call":
        breakeven = round(max(0.0, stock_entry - args.premium), 2)
        max_profit = round(((args.strike - stock_entry) + args.premium) * scale, 2)
        max_loss = round((-stock_entry + args.premium) * scale, 2)
    else:  # protective_put
        breakeven = round(stock_entry + args.premium, 2)
        max_profit = "Unlimited"
        max_loss = round(((args.strike - stock_entry) - args.premium) * scale, 2)

    return {
        "strategy": args.strategy,
        "strike": round(args.strike, 2),
        "premium": round(args.premium, 2),
        "stock_entry": round(stock_entry, 2) if args.strategy in ("covered_call", "protective_put") else None,
        "contracts": args.contracts,
        "multiplier": args.multiplier,
        "breakeven": breakeven,
        "max_profit": max_profit,
        "max_loss": max_loss,
        "payoff_grid": grid,
    }


def cmd_llm_cost(args: argparse.Namespace) -> dict[str, Any]:
    if args.cached_tokens > args.input_tokens:
        raise ValueError("--cached-tokens cannot exceed --input-tokens.")
    uncached_input = args.input_tokens - args.cached_tokens
    input_cost = (uncached_input / 1_000_000.0) * args.input_price_per_1m
    cached_cost = (args.cached_tokens / 1_000_000.0) * args.cached_price_per_1m
    output_cost = (args.output_tokens / 1_000_000.0) * args.output_price_per_1m
    per_run = input_cost + cached_cost + output_cost
    daily = per_run * args.daily_runs
    monthly = daily * 30.0
    return {
        "input_tokens": args.input_tokens,
        "cached_tokens": args.cached_tokens,
        "output_tokens": args.output_tokens,
        "daily_runs": args.daily_runs,
        "cost_per_run": round(per_run, 6),
        "daily_cost": round(daily, 4),
        "monthly_30d_cost": round(monthly, 2),
    }


def _format_text(command: str, data: dict[str, Any]) -> str:
    if command == "cagr":
        return (
            f"Return Analysis ({data['years']} yrs): "
            f"Total {data['total_return_pct']:+.2f}% | CAGR {data['cagr_pct']:+.2f}% "
            f"({data['start_value']} -> {data['end_value']})"
        )
    if command == "allocation":
        lines = [
            f"Portfolio Rebalance (Current: {data['current_total']}, "
            f"Contribution: {data['contribution']}, Target Total: {data['projected_total']}):"
        ]
        for row in data["positions"]:
            lines.append(
                f"- {row['asset']}: {row['current_pct']}% vs {row['target_pct']}% "
                f"(drift {row['drift_pct']:+.2f}%) -> trade {row['rebalance_delta']:+.2f}"
            )
        return "\n".join(lines)
    if command == "options-payoff":
        lines = [
            f"Options Payoff ({data['strategy']}, strike {data['strike']}, premium {data['premium']}, "
            f"{data['contracts']}x{data['multiplier']}):",
            f"- Breakeven: {data['breakeven']} | Max Profit: {data['max_profit']} | Max Loss: {data['max_loss']}",
        ]
        for pt in data["payoff_grid"]:
            lines.append(f"  Spot {pt['spot']:>8.2f} -> PnL {pt['pnl']:+.2f}")
        return "\n".join(lines)
    return "\n".join([
        f"LLM Inference Cost ({data['daily_runs']} runs/day):",
        f"- Per Run: ${data['cost_per_run']:.6f}",
        f"- Daily:   ${data['daily_cost']:.4f}",
        f"- 30-Day:  ${data['monthly_30d_cost']:.2f}",
    ])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plutus deterministic finance, portfolio, options, and LLM cost CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    cagr = subparsers.add_parser("cagr", help="Compute total return and Compound Annual Growth Rate.")
    cagr.add_argument("--start-value", type=_positive_float, required=True, help="Initial portfolio/asset value.")
    cagr.add_argument("--end-value", type=_positive_float, required=True, help="Ending portfolio/asset value.")
    cagr.add_argument("--years", type=_positive_float, required=True, help="Holding period in years.")
    cagr.add_argument("--json", action="store_true", help="Emit JSON output.")

    alloc = subparsers.add_parser("allocation", help="Compute target drift and rebalance trades from portfolio JSON.")
    alloc.add_argument("--portfolio-json", required=True, help="Path to JSON array of holdings (or '-' for stdin).")
    alloc.add_argument("--contribution", type=_non_negative_float, default=0.0, help="New cash added to allocate.")
    alloc.add_argument("--json", action="store_true", help="Emit JSON output.")

    opt = subparsers.add_parser("options-payoff", help="Compute expiration payoff grid, breakeven, max profit, and max loss.")
    opt.add_argument("--strategy", choices=STRATEGIES, required=True, help="Option strategy type.")
    opt.add_argument("--strike", type=_positive_float, required=True, help="Option strike price.")
    opt.add_argument("--premium", type=_non_negative_float, required=True, help="Option premium per share.")
    opt.add_argument("--stock-entry", type=_positive_float, help="Underlying entry price (required for covered_call/protective_put).")
    opt.add_argument("--contracts", type=_positive_int, default=1, help="Number of option contracts (default: 1).")
    opt.add_argument("--multiplier", type=_positive_int, default=100, help="Shares per contract (default: 100).")
    opt.add_argument("--spot-min", type=_non_negative_float, help="Minimum spot price for payoff grid.")
    opt.add_argument("--spot-max", type=_positive_float, help="Maximum spot price for payoff grid.")
    opt.add_argument("--steps", type=_positive_int, default=6, help="Number of grid intervals (default: 6).")
    opt.add_argument("--json", action="store_true", help="Emit JSON output.")

    llm = subparsers.add_parser("llm-cost", help="Project per-run, daily, and 30-day LLM inference costs.")
    llm.add_argument("--input-tokens", type=int, required=True, help="Total prompt/input tokens per run.")
    llm.add_argument("--output-tokens", type=int, required=True, help="Output/completion tokens per run.")
    llm.add_argument("--input-price-per-1m", type=_non_negative_float, required=True, help="Price per 1M uncached input tokens.")
    llm.add_argument("--output-price-per-1m", type=_non_negative_float, required=True, help="Price per 1M output tokens.")
    llm.add_argument("--cached-tokens", type=int, default=0, help="Cached input tokens per run (subset of --input-tokens).")
    llm.add_argument("--cached-price-per-1m", type=_non_negative_float, default=0.0, help="Price per 1M cached input tokens.")
    llm.add_argument("--daily-runs", type=_positive_int, default=1, help="Estimated runs per day (default: 1).")
    llm.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "cagr":
            result = cmd_cagr(args)
        elif args.command == "allocation":
            result = cmd_allocation(args)
        elif args.command == "options-payoff":
            result = cmd_options_payoff(args)
        else:
            result = cmd_llm_cost(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_text(args.command, result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
