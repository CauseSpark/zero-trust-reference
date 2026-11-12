"""Consistency checks on the repo's data files and docs.

These keep the worksheet, the 800-53 mapping and the diagrams in sync as they change.
"""

import csv
import re
from pathlib import Path

import pytest

from src import maturity_score as ms

ROOT = Path(__file__).resolve().parents[1]
WORKSHEET = ROOT / "assessment" / "maturity_worksheet.csv"
MAPPING = ROOT / "mapping" / "zt_to_800-53.csv"
DIAGRAMS = ROOT / "diagrams"

# The 20 control families in SP 800-53 Rev 5.
FAMILIES_800_53 = {
    "AC", "AT", "AU", "CA", "CM", "CP", "IA", "IR", "MA", "MP",
    "PE", "PL", "PM", "PS", "PT", "RA", "SA", "SC", "SI", "SR",
}
CONTROL_RE = re.compile(r"^(?P<family>[A-Z]{2})-(?P<num>\d{1,2})(\((?P<enh>\d{1,2})\))?$")
TENET_RE = re.compile(r"^T[1-7]$")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@pytest.fixture(scope="module")
def worksheet():
    return read_csv(WORKSHEET)


@pytest.fixture(scope="module")
def mapping():
    return read_csv(MAPPING)


def test_worksheet_loads_cleanly():
    caps = ms.load_worksheet(WORKSHEET)
    assert len(caps) >= 20


def test_worksheet_covers_every_pillar(worksheet):
    assert {r["pillar"] for r in worksheet} == set(ms.PILLARS)


def test_worksheet_id_prefix_matches_pillar(worksheet):
    prefixes = {
        "Identity": "ID-",
        "Devices": "DV-",
        "Networks": "NW-",
        "Applications and Workloads": "AW-",
        "Data": "DA-",
        "Cross-Cutting": "CC-",
    }
    for r in worksheet:
        assert r["capability_id"].startswith(prefixes[r["pillar"]]), r["capability_id"]


def test_mapping_ids_match_worksheet_exactly(worksheet, mapping):
    ws = {r["capability_id"]: (r["pillar"], r["function"]) for r in worksheet}
    mp = {r["capability_id"]: (r["pillar"], r["function"]) for r in mapping}
    assert ws == mp, "worksheet and mapping must list the same capabilities with the same pillar/function"


def test_mapping_has_no_duplicate_ids(mapping):
    ids = [r["capability_id"] for r in mapping]
    assert len(ids) == len(set(ids))


def test_control_ids_are_well_formed(mapping):
    for r in mapping:
        controls = r["nist_800_53_rev5_controls"].split(";")
        assert controls and all(controls), f"{r['capability_id']}: empty control list"
        assert len(controls) == len(set(controls)), f"{r['capability_id']}: duplicate control"
        for c in controls:
            m = CONTROL_RE.match(c)
            assert m, f"{r['capability_id']}: malformed control {c!r}"
            assert m["family"] in FAMILIES_800_53, f"{r['capability_id']}: unknown family in {c!r}"


def test_tenets_are_valid(mapping):
    for r in mapping:
        tenets = r["nist_800_207_tenets"].split(";")
        assert tenets and all(TENET_RE.match(t) for t in tenets), r["capability_id"]


def test_every_tenet_is_covered(mapping):
    covered = {t for r in mapping for t in r["nist_800_207_tenets"].split(";")}
    assert covered == {f"T{i}" for i in range(1, 8)}


def test_every_mapping_has_rationale(mapping):
    for r in mapping:
        assert len(r["mapping_rationale"].split()) >= 5, r["capability_id"]


def test_diagrams_contain_mermaid_blocks():
    files = sorted(DIAGRAMS.glob("[0-9][0-9]_*.md"))
    assert len(files) >= 3
    for f in files:
        text = f.read_text(encoding="utf-8")
        assert text.count("```mermaid") >= 1, f.name
        assert text.count("```") % 2 == 0, f"{f.name}: unbalanced code fences"


def test_diagram_index_lists_every_diagram():
    index = (DIAGRAMS / "README.md").read_text(encoding="utf-8")
    for f in DIAGRAMS.glob("[0-9][0-9]_*.md"):
        assert f.name in index, f"{f.name} missing from diagrams/README.md"
