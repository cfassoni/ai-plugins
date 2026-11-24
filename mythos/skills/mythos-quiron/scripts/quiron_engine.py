#!/usr/bin/env python3
"""Deterministic fitness, biomechanics, and MET + RPE/RIR + EPOC calorie engine for Mythos Quiron."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"Value must be > 0, got {value}")
    return parsed


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"Value must be > 0, got {value}")
    return parsed


def _resolve_rpe(rpe: float | None, rir: float | None, default: float = 8.0) -> float:
    if rpe is not None and rir is not None:
        raise ValueError("Specify either RPE or RIR, not both.")
    if rpe is not None:
        if not 1.0 <= rpe <= 10.0:
            raise ValueError(f"RPE must be between 1.0 and 10.0, got {rpe}")
        return rpe
    if rir is not None:
        if not 0.0 <= rir <= 9.0:
            raise ValueError(f"RIR must be between 0.0 and 9.0, got {rir}")
        return 10.0 - rir
    return default


def _rpe_modifier(rpe: float) -> float:
    if rpe < 6.0:
        return 0.80
    if rpe <= 8.0:
        return 1.00
    if rpe < 9.75:
        return 1.25
    return 1.40


def _auto_epoc_factor(avg_rpe: float, working_sets: int) -> float:
    intensity_norm = max(0.0, min(1.0, (avg_rpe - 6.0) / 4.0))
    volume_norm = max(0.0, min(1.0, working_sets / 24.0))
    score = 0.70 * intensity_norm + 0.30 * volume_norm
    return round(0.08 + 0.06 * score, 4)


def _load_sets(sets_json: str) -> list[dict[str, Any]]:
    raw = sys.stdin.read() if sets_json == "-" else Path(sets_json).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list) or not data:
        raise ValueError("Sets JSON must be a non-empty JSON array.")
    return data


def _kcal_per_min(effective_met: float, body_weight_kg: float) -> float:
    return (effective_met * 3.5 * body_weight_kg) / 200.0


def cmd_calories(args: argparse.Namespace) -> dict[str, Any]:
    if args.epoc_factor is not None and not 0.0 <= args.epoc_factor <= 0.30:
        raise ValueError(f"EPOC factor must be between 0.0 and 0.30, got {args.epoc_factor}")

    if args.sets_json:
        sets = _load_sets(args.sets_json)
        total_duration = 0.0
        intra_kcal = 0.0
        rpes: list[float] = []
        working_sets = 0
        default_set_duration = (args.duration_min / len(sets)) if args.duration_min else 2.5

        for idx, item in enumerate(sets, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Set #{idx} must be a JSON object.")
            rpe = _resolve_rpe(
                float(item["rpe"]) if "rpe" in item and item["rpe"] is not None else None,
                float(item["rir"]) if "rir" in item and item["rir"] is not None else None,
                default=8.0,
            )
            set_duration = float(item.get("duration_min", default_set_duration))
            if set_duration <= 0:
                raise ValueError(f"Set #{idx} duration_min must be > 0.")
            eff_met = args.base_met * _rpe_modifier(rpe)
            intra_kcal += _kcal_per_min(eff_met, args.body_weight_kg) * set_duration
            total_duration += set_duration
            rpes.append(rpe)
            if rpe >= 6.0:
                working_sets += 1

        avg_rpe = sum(rpes) / len(rpes)
        epoc_factor = (
            args.epoc_factor
            if args.epoc_factor is not None
            else _auto_epoc_factor(avg_rpe, working_sets)
        )
        effective_met = args.base_met * _rpe_modifier(avg_rpe)
        mode = "per-set"
    else:
        if args.duration_min is None:
            raise ValueError("Summary mode requires --duration-min when --sets-json is omitted.")
        avg_rpe = _resolve_rpe(args.avg_rpe, args.avg_rir, default=8.0)
        modifier = _rpe_modifier(avg_rpe)
        effective_met = args.base_met * modifier
        total_duration = args.duration_min
        intra_kcal = _kcal_per_min(effective_met, args.body_weight_kg) * total_duration
        estimated_sets = max(1, round(total_duration / 2.5))
        epoc_factor = (
            args.epoc_factor
            if args.epoc_factor is not None
            else _auto_epoc_factor(avg_rpe, estimated_sets)
        )
        mode = "summary"

    epoc_kcal = intra_kcal * epoc_factor
    total_kcal = intra_kcal + epoc_kcal
    return {
        "mode": mode,
        "body_weight_kg": round(args.body_weight_kg, 2),
        "duration_min": round(total_duration, 2),
        "base_met": round(args.base_met, 2),
        "avg_rpe": round(avg_rpe, 2),
        "effective_met": round(effective_met, 2),
        "intra_workout_kcal": round(intra_kcal, 1),
        "epoc_factor": round(epoc_factor, 4),
        "epoc_kcal": round(epoc_kcal, 1),
        "total_kcal": round(total_kcal, 1),
    }


def cmd_e1rm(args: argparse.Namespace) -> dict[str, Any]:
    rpe = _resolve_rpe(args.rpe, args.rir, default=10.0) if (args.rpe is not None or args.rir is not None) else None
    rir = (10.0 - rpe) if rpe is not None else 0.0
    effective_reps = args.reps + rir

    if effective_reps == 1:
        epley = args.weight
        brzycki = args.weight
    else:
        epley = args.weight * (1.0 + effective_reps / 30.0)
        if effective_reps >= 37:
            raise ValueError("Brzycki formula requires effective reps < 37.")
        brzycki = args.weight * 36.0 / (37.0 - effective_reps)

    avg_e1rm = (epley + brzycki) / 2.0
    percentages = {
        f"{pct}%": round(avg_e1rm * (pct / 100.0), 1)
        for pct in (95, 90, 85, 80, 75, 70, 65, 60)
    }
    return {
        "weight": round(args.weight, 2),
        "reps": args.reps,
        "rpe": round(rpe, 2) if rpe is not None else None,
        "effective_reps": round(effective_reps, 2),
        "epley_1rm": round(epley, 1),
        "brzycki_1rm": round(brzycki, 1),
        "average_1rm": round(avg_e1rm, 1),
        "working_weights": percentages,
    }


def cmd_volume(args: argparse.Namespace) -> dict[str, Any]:
    sets = _load_sets(args.sets_json)
    total_reps = 0
    tonnage = 0.0
    rpes: list[float] = []
    exercises: dict[str, dict[str, float]] = {}

    for idx, item in enumerate(sets, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Set #{idx} must be a JSON object.")
        weight = float(item.get("weight_kg", item.get("weight", 0.0)))
        reps = int(item.get("reps", 0))
        if weight < 0 or reps <= 0:
            raise ValueError(f"Set #{idx} requires weight >= 0 and reps > 0.")
        total_reps += reps
        set_tonnage = weight * reps
        tonnage += set_tonnage

        if "rpe" in item or "rir" in item:
            rpe = _resolve_rpe(
                float(item["rpe"]) if item.get("rpe") is not None else None,
                float(item["rir"]) if item.get("rir") is not None else None,
                default=8.0,
            )
            rpes.append(rpe)

        name = str(item.get("exercise", "Unspecified"))
        entry = exercises.setdefault(name, {"sets": 0, "reps": 0, "tonnage_kg": 0.0})
        entry["sets"] += 1
        entry["reps"] += reps
        entry["tonnage_kg"] = round(entry["tonnage_kg"] + set_tonnage, 2)

    return {
        "total_sets": len(sets),
        "total_reps": total_reps,
        "total_tonnage_kg": round(tonnage, 2),
        "avg_load_kg": round(tonnage / total_reps, 2) if total_reps else 0.0,
        "avg_rpe": round(sum(rpes) / len(rpes), 2) if rpes else None,
        "by_exercise": exercises,
    }


def _format_text(command: str, data: dict[str, Any]) -> str:
    if command == "calories":
        return "\n".join([
            f"Calorie Expenditure ({data['mode']} mode):",
            f"- Body Weight: {data['body_weight_kg']} kg | Duration: {data['duration_min']} min",
            f"- Avg RPE: {data['avg_rpe']} | Effective MET: {data['effective_met']} (base {data['base_met']})",
            f"- Intra-Workout: {data['intra_workout_kcal']} kcal",
            f"- EPOC (+{data['epoc_factor'] * 100:.1f}%): {data['epoc_kcal']} kcal",
            f"- Total Expenditure: {data['total_kcal']} kcal",
        ])
    if command == "e1rm":
        table = ", ".join(f"{k}: {v}" for k, v in data["working_weights"].items())
        return "\n".join([
            f"Estimated 1RM ({data['weight']} x {data['reps']} reps, effective {data['effective_reps']}):",
            f"- Epley: {data['epley_1rm']} | Brzycki: {data['brzycki_1rm']} | Average: {data['average_1rm']}",
            f"- Load Table: {table}",
        ])
    lines = [
        "Workout Volume Summary:",
        f"- Sets: {data['total_sets']} | Reps: {data['total_reps']} | Tonnage: {data['total_tonnage_kg']} kg",
        f"- Avg Load/Rep: {data['avg_load_kg']} kg | Avg RPE: {data['avg_rpe']}",
    ]
    for ex, stats in data["by_exercise"].items():
        lines.append(f"  - {ex}: {stats['sets']} sets, {stats['reps']} reps, {stats['tonnage_kg']} kg")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Quiron physiological calorie (MET + RPE + EPOC) and strength analytics CLI."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    cal = subparsers.add_parser("calories", help="Estimate resistance training expenditure with MET + RPE + EPOC.")
    cal.add_argument("--body-weight-kg", type=_positive_float, required=True, help="Body weight in kilograms.")
    cal.add_argument("--duration-min", type=_positive_float, help="Session duration in minutes (required in summary mode).")
    cal.add_argument("--avg-rpe", type=float, help="Average session RPE (1.0-10.0).")
    cal.add_argument("--avg-rir", type=float, help="Average session RIR (0.0-9.0).")
    cal.add_argument("--base-met", type=_positive_float, default=6.0, help="Base resistance training MET (default: 6.0).")
    cal.add_argument("--epoc-factor", type=float, help="Override EPOC multiplier (e.g. 0.11 for +11%%).")
    cal.add_argument("--sets-json", help="Optional path to JSON array of sets (or '-' for stdin).")
    cal.add_argument("--json", action="store_true", help="Emit JSON output.")

    erm = subparsers.add_parser("e1rm", help="Compute Epley and Brzycki estimated 1RM and %%1RM load table.")
    erm.add_argument("--weight", type=_positive_float, required=True, help="Load lifted (kg or lb).")
    erm.add_argument("--reps", type=_positive_int, required=True, help="Repetitions completed.")
    erm.add_argument("--rpe", type=float, help="Set RPE (1.0-10.0) to adjust effective reps.")
    erm.add_argument("--rir", type=float, help="Set RIR (0.0-9.0) to adjust effective reps.")
    erm.add_argument("--json", action="store_true", help="Emit JSON output.")

    vol = subparsers.add_parser("volume", help="Summarize total sets, reps, tonnage, and per-exercise volume.")
    vol.add_argument("--sets-json", required=True, help="Path to JSON array of sets (or '-' for stdin).")
    vol.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "calories":
            result = cmd_calories(args)
        elif args.command == "e1rm":
            result = cmd_e1rm(args)
        else:
            result = cmd_volume(args)
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
