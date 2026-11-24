#!/usr/bin/env python3
"""Deterministic BMR (Mifflin-St Jeor), TDEE, and macronutrient calculator for Mythos Higia."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"Value must be > 0, got {value}")
    return parsed


def _compute_bmr(sex: str, weight_kg: float, height_cm: float, age: float) -> float:
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    return base + 5.0 if sex == "male" else base - 161.0


def cmd_bmr(args: argparse.Namespace) -> dict[str, Any]:
    bmr = _compute_bmr(args.sex, args.weight_kg, args.height_cm, args.age)
    return {
        "formula": "Mifflin-St Jeor",
        "sex": args.sex,
        "weight_kg": round(args.weight_kg, 2),
        "height_cm": round(args.height_cm, 1),
        "age": round(args.age, 1),
        "bmr_kcal": round(bmr, 1),
    }


def cmd_tdee(args: argparse.Namespace) -> dict[str, Any]:
    if args.delta_kcal is not None and args.delta_pct is not None:
        raise ValueError("Specify either --delta-kcal or --delta-pct, not both.")
    bmr = _compute_bmr(args.sex, args.weight_kg, args.height_cm, args.age)
    factor = ACTIVITY_FACTORS[args.activity]
    tdee = bmr * factor
    if args.delta_kcal is not None:
        target = tdee + args.delta_kcal
    elif args.delta_pct is not None:
        target = tdee * (1.0 + args.delta_pct / 100.0)
    else:
        target = tdee

    if target <= 0:
        raise ValueError(f"Target calories must remain > 0, got {target:.1f}")
    return {
        "bmr_kcal": round(bmr, 1),
        "activity": args.activity,
        "activity_factor": factor,
        "tdee_kcal": round(tdee, 1),
        "target_kcal": round(target, 1),
        "delta_kcal": round(target - tdee, 1),
    }


def cmd_macros(args: argparse.Namespace) -> dict[str, Any]:
    if not 0.05 <= args.fat_pct <= 0.65:
        raise ValueError(f"--fat-pct must be between 0.05 and 0.65, got {args.fat_pct}")

    if args.weight_kg is not None:
        protein_g = args.weight_kg * args.protein_g_per_kg
        protein_kcal = protein_g * 4.0
        protein_source = f"{args.protein_g_per_kg} g/kg x {args.weight_kg} kg"
    else:
        if not 0.05 <= args.protein_pct <= 0.65:
            raise ValueError(f"--protein-pct must be between 0.05 and 0.65, got {args.protein_pct}")
        protein_kcal = args.calories * args.protein_pct
        protein_g = protein_kcal / 4.0
        protein_source = f"{args.protein_pct * 100:.1f}% of calories"

    fat_kcal = args.calories * args.fat_pct
    fat_g = fat_kcal / 9.0
    carbs_kcal = args.calories - protein_kcal - fat_kcal
    if carbs_kcal < 0:
        raise ValueError(
            f"Protein ({protein_kcal:.0f} kcal) + Fat ({fat_kcal:.0f} kcal) exceed total calories ({args.calories:.0f} kcal)."
        )
    carbs_g = carbs_kcal / 4.0

    return {
        "calories": round(args.calories, 1),
        "protein_source": protein_source,
        "protein_g": round(protein_g, 1),
        "protein_kcal": round(protein_kcal, 1),
        "protein_pct": round((protein_kcal / args.calories) * 100.0, 1),
        "fat_g": round(fat_g, 1),
        "fat_kcal": round(fat_kcal, 1),
        "fat_pct": round((fat_kcal / args.calories) * 100.0, 1),
        "carbs_g": round(carbs_g, 1),
        "carbs_kcal": round(carbs_kcal, 1),
        "carbs_pct": round((carbs_kcal / args.calories) * 100.0, 1),
    }


def _format_text(command: str, data: dict[str, Any]) -> str:
    if command == "bmr":
        return f"BMR ({data['formula']}, {data['sex']}): {data['bmr_kcal']} kcal/day"
    if command == "tdee":
        return "\n".join([
            f"Energy Balance ({data['activity']}, factor {data['activity_factor']}x):",
            f"- BMR: {data['bmr_kcal']} kcal/day",
            f"- Maintenance TDEE: {data['tdee_kcal']} kcal/day",
            f"- Target Intake: {data['target_kcal']} kcal/day (delta {data['delta_kcal']:+.1f} kcal)",
        ])
    return "\n".join([
        f"Macro Split ({data['calories']} kcal | {data['protein_source']}):",
        f"- Protein: {data['protein_g']} g ({data['protein_kcal']} kcal, {data['protein_pct']}%)",
        f"- Fat:     {data['fat_g']} g ({data['fat_kcal']} kcal, {data['fat_pct']}%)",
        f"- Carbs:   {data['carbs_g']} g ({data['carbs_kcal']} kcal, {data['carbs_pct']}%)",
    ])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Higia deterministic BMR, TDEE, and macronutrient calculator.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("bmr", "Compute Basal Metabolic Rate (Mifflin-St Jeor)."),
        ("tdee", "Compute Total Daily Energy Expenditure and target intake."),
    ):
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument("--sex", choices=("male", "female"), required=True, help="Biological sex for Mifflin-St Jeor.")
        sub.add_argument("--weight-kg", type=_positive_float, required=True, help="Body weight in kilograms.")
        sub.add_argument("--height-cm", type=_positive_float, required=True, help="Height in centimeters.")
        sub.add_argument("--age", type=_positive_float, required=True, help="Age in years.")
        if name == "tdee":
            sub.add_argument("--activity", choices=tuple(ACTIVITY_FACTORS), required=True, help="Activity multiplier tier.")
            sub.add_argument("--delta-kcal", type=float, help="Signed calorie adjustment (e.g. -400 or +250).")
            sub.add_argument("--delta-pct", type=float, help="Signed percentage adjustment (e.g. -15 or +10).")
        sub.add_argument("--json", action="store_true", help="Emit JSON output.")

    mac = subparsers.add_parser("macros", help="Compute daily protein, fat, and carbohydrate targets.")
    mac.add_argument("--calories", type=_positive_float, required=True, help="Target daily calories.")
    mac.add_argument("--weight-kg", type=_positive_float, help="Optional body weight to anchor protein g/kg.")
    mac.add_argument("--protein-g-per-kg", type=_positive_float, default=1.8, help="Protein target in g/kg (default: 1.8).")
    mac.add_argument("--protein-pct", type=float, default=0.30, help="Protein share if --weight-kg omitted (default: 0.30).")
    mac.add_argument("--fat-pct", type=float, default=0.25, help="Dietary fat share of calories (default: 0.25).")
    mac.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "bmr":
            result = cmd_bmr(args)
        elif args.command == "tdee":
            result = cmd_tdee(args)
        else:
            result = cmd_macros(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_text(args.command, result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
