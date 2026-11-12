"""Score a zero trust maturity worksheet that uses CISA ZTMM v2.0 stages.

Reads a CSV with one row per capability (ZTMM function) and reports, per pillar:

* weighted mean of the current stage (1 = Traditional ... 4 = Optimal)
* a 0-100 maturity index derived from that mean
* the *floor* stage, meaning the lowest stage of any function in the pillar. A pillar is
  only as mature as its weakest function, so the floor is often the more honest number.
* weighted gap to target

It also lists the largest weighted gaps, so they can be prioritized.

Usage::

    python -m src.maturity_score assessment/maturity_worksheet.csv
    python -m src.maturity_score assessment/maturity_worksheet.csv --format json
    python -m src.maturity_score assessment/maturity_worksheet.csv --top 5

Standard library only. This is personal study material, not an official CISA scoring method.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

STAGES: dict[str, int] = {
    "Traditional": 1,
    "Initial": 2,
    "Advanced": 3,
    "Optimal": 4,
}
STAGE_NAMES: dict[int, str] = {v: k for k, v in STAGES.items()}

PILLARS: tuple[str, ...] = (
    "Identity",
    "Devices",
    "Networks",
    "Applications and Workloads",
    "Data",
    "Cross-Cutting",
)

REQUIRED_COLUMNS: tuple[str, ...] = (
    "capability_id",
    "pillar",
    "function",
    "current_stage",
    "target_stage",
    "weight",
)


class WorksheetError(ValueError):
    """Raised when the worksheet is malformed."""


@dataclass(frozen=True)
class Capability:
    capability_id: str
    pillar: str
    function: str
    current: int
    target: int
    weight: float

    @property
    def gap(self) -> int:
        return self.target - self.current

    @property
    def weighted_gap(self) -> float:
        return self.gap * self.weight


@dataclass(frozen=True)
class PillarScore:
    pillar: str
    capabilities: int
    mean_stage: float
    maturity_index: float
    floor_stage: str
    mean_gap: float


@dataclass(frozen=True)
class Report:
    overall_mean_stage: float
    overall_maturity_index: float
    pillars: list[PillarScore]
    top_gaps: list[dict]


def parse_stage(value: str, *, row: int, column: str) -> int:
    """Convert a stage name (case-insensitive) or 1-4 integer into its numeric value."""
    text = (value or "").strip()
    if text.isdigit() and int(text) in STAGE_NAMES:
        return int(text)
    for name, num in STAGES.items():
        if text.lower() == name.lower():
            return num
    raise WorksheetError(
        f"row {row}: invalid {column} {value!r}; expected one of {list(STAGES)} or 1-4"
    )


def parse_rows(rows: Iterable[dict], fieldnames: Iterable[str] | None) -> list[Capability]:
    """Validate raw CSV rows and convert them into Capability objects."""
    fields = set(fieldnames or [])
    missing = [c for c in REQUIRED_COLUMNS if c not in fields]
    if missing:
        raise WorksheetError(f"missing required column(s): {', '.join(missing)}")

    caps: list[Capability] = []
    seen: set[str] = set()
    # Row 1 is the header, so data starts at row 2 (matches what a spreadsheet shows).
    for i, raw in enumerate(rows, start=2):
        cid = (raw.get("capability_id") or "").strip()
        if not cid:
            raise WorksheetError(f"row {i}: capability_id is empty")
        if cid in seen:
            raise WorksheetError(f"row {i}: duplicate capability_id {cid!r}")
        seen.add(cid)

        pillar = (raw.get("pillar") or "").strip()
        if pillar not in PILLARS:
            raise WorksheetError(f"row {i}: unknown pillar {pillar!r}; expected one of {list(PILLARS)}")

        current = parse_stage(raw.get("current_stage", ""), row=i, column="current_stage")
        target = parse_stage(raw.get("target_stage", ""), row=i, column="target_stage")
        if target < current:
            raise WorksheetError(
                f"row {i}: target_stage ({STAGE_NAMES[target]}) is below current_stage "
                f"({STAGE_NAMES[current]}) for {cid}"
            )

        try:
            weight = float((raw.get("weight") or "").strip())
        except ValueError:
            raise WorksheetError(f"row {i}: weight {raw.get('weight')!r} is not a number") from None
        if weight <= 0:
            raise WorksheetError(f"row {i}: weight must be positive, got {weight}")

        caps.append(
            Capability(
                capability_id=cid,
                pillar=pillar,
                function=(raw.get("function") or "").strip(),
                current=current,
                target=target,
                weight=weight,
            )
        )

    if not caps:
        raise WorksheetError("worksheet has no data rows")
    return caps


def load_worksheet(path: str | Path) -> list[Capability]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return parse_rows(reader, reader.fieldnames)


def maturity_index(mean_stage: float) -> float:
    """Map a 1-4 stage mean onto 0-100 (Traditional = 0, Optimal = 100)."""
    return round((mean_stage - 1) / 3 * 100, 1)


def _weighted_mean(values: Iterable[tuple[float, float]]) -> float:
    pairs = list(values)
    total_w = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / total_w


def score(caps: list[Capability], top: int = 5) -> Report:
    pillar_scores: list[PillarScore] = []
    for pillar in PILLARS:
        group = [c for c in caps if c.pillar == pillar]
        if not group:
            continue
        mean = _weighted_mean((c.current, c.weight) for c in group)
        gap = _weighted_mean((c.gap, c.weight) for c in group)
        pillar_scores.append(
            PillarScore(
                pillar=pillar,
                capabilities=len(group),
                mean_stage=round(mean, 2),
                maturity_index=maturity_index(mean),
                floor_stage=STAGE_NAMES[min(c.current for c in group)],
                mean_gap=round(gap, 2),
            )
        )

    overall = _weighted_mean((c.current, c.weight) for c in caps)
    ranked = sorted(
        (c for c in caps if c.gap > 0),
        key=lambda c: (-c.weighted_gap, c.capability_id),
    )[: max(top, 0)]
    top_gaps = [
        {
            "capability_id": c.capability_id,
            "pillar": c.pillar,
            "function": c.function,
            "current": STAGE_NAMES[c.current],
            "target": STAGE_NAMES[c.target],
            "weighted_gap": round(c.weighted_gap, 2),
        }
        for c in ranked
    ]
    return Report(
        overall_mean_stage=round(overall, 2),
        overall_maturity_index=maturity_index(overall),
        pillars=pillar_scores,
        top_gaps=top_gaps,
    )


def to_markdown(report: Report) -> str:
    lines = [
        "# Zero Trust Maturity Summary",
        "",
        f"**Overall:** mean stage {report.overall_mean_stage:.2f} / 4 "
        f"· maturity index {report.overall_maturity_index:.1f} / 100",
        "",
        "| Pillar | Functions | Mean stage | Index | Floor stage | Mean gap |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for p in report.pillars:
        lines.append(
            f"| {p.pillar} | {p.capabilities} | {p.mean_stage:.2f} | {p.maturity_index:.1f} "
            f"| {p.floor_stage} | {p.mean_gap:.2f} |"
        )
    lines += ["", "## Top weighted gaps", ""]
    if report.top_gaps:
        lines += ["| ID | Pillar | Function | Current → Target | Weighted gap |", "|---|---|---|---|---:|"]
        for g in report.top_gaps:
            lines.append(
                f"| {g['capability_id']} | {g['pillar']} | {g['function']} "
                f"| {g['current']} → {g['target']} | {g['weighted_gap']:.1f} |"
            )
    else:
        lines.append("No open gaps. Every function is at its target stage.")
    return "\n".join(lines) + "\n"


def to_json(report: Report) -> str:
    return json.dumps(asdict(report), indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("worksheet", help="path to maturity worksheet CSV")
    parser.add_argument("--format", choices=("md", "json"), default="md")
    parser.add_argument("--top", type=int, default=5, help="number of gaps to list (default 5)")
    args = parser.parse_args(argv)

    try:
        report = score(load_worksheet(args.worksheet), top=args.top)
    except (OSError, WorksheetError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    sys.stdout.write(to_json(report) if args.format == "json" else to_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
