import csv
import io
import json
from pathlib import Path

import pytest

from src import maturity_score as ms

ROOT = Path(__file__).resolve().parents[1]
WORKSHEET = ROOT / "assessment" / "maturity_worksheet.csv"

HEADER = "capability_id,pillar,function,current_stage,target_stage,weight\n"


def parse(text: str):
    reader = csv.DictReader(io.StringIO(text))
    return ms.parse_rows(reader, reader.fieldnames)


# --- parse_stage ---------------------------------------------------------

@pytest.mark.parametrize(
    "value,expected",
    [("Traditional", 1), ("initial", 2), ("ADVANCED", 3), (" Optimal ", 4), ("3", 3)],
)
def test_parse_stage_accepts_names_and_numbers(value, expected):
    assert ms.parse_stage(value, row=2, column="current_stage") == expected


@pytest.mark.parametrize("value", ["", "Expert", "0", "5", "2.5"])
def test_parse_stage_rejects_invalid(value):
    with pytest.raises(ms.WorksheetError, match="row 2"):
        ms.parse_stage(value, row=2, column="current_stage")


# --- validation ----------------------------------------------------------

def test_missing_column_is_reported():
    with pytest.raises(ms.WorksheetError, match="weight"):
        parse("capability_id,pillar,function,current_stage,target_stage\nX,Data,f,Initial,Initial\n")


def test_unknown_pillar_rejected():
    with pytest.raises(ms.WorksheetError, match="unknown pillar"):
        parse(HEADER + "X-1,Perimeter,f,Initial,Advanced,1\n")


def test_duplicate_id_rejected():
    with pytest.raises(ms.WorksheetError, match="duplicate"):
        parse(HEADER + "X-1,Data,a,Initial,Advanced,1\nX-1,Data,b,Initial,Advanced,1\n")


def test_target_below_current_rejected():
    with pytest.raises(ms.WorksheetError, match="below current_stage"):
        parse(HEADER + "X-1,Data,f,Advanced,Initial,1\n")


@pytest.mark.parametrize("weight", ["0", "-1", "heavy", ""])
def test_bad_weight_rejected(weight):
    with pytest.raises(ms.WorksheetError, match="weight"):
        parse(HEADER + f"X-1,Data,f,Initial,Advanced,{weight}\n")


def test_empty_worksheet_rejected():
    with pytest.raises(ms.WorksheetError, match="no data rows"):
        parse(HEADER)


# --- scoring math --------------------------------------------------------

def test_maturity_index_endpoints():
    assert ms.maturity_index(1) == 0.0
    assert ms.maturity_index(4) == 100.0
    assert ms.maturity_index(2.5) == 50.0


def test_weighted_mean_and_floor():
    caps = parse(
        HEADER
        + "D-1,Data,a,Traditional,Advanced,1\n"  # 1, gap 2
        + "D-2,Data,b,Optimal,Optimal,3\n"       # 4, gap 0
    )
    report = ms.score(caps)
    (data,) = report.pillars
    # (1*1 + 4*3) / 4 = 3.25
    assert data.mean_stage == 3.25
    assert data.maturity_index == 75.0
    assert data.floor_stage == "Traditional"
    # (2*1 + 0*3) / 4 = 0.5
    assert data.mean_gap == 0.5


def test_pillars_without_rows_are_omitted():
    caps = parse(HEADER + "I-1,Identity,a,Initial,Advanced,1\n")
    report = ms.score(caps)
    assert [p.pillar for p in report.pillars] == ["Identity"]


def test_top_gaps_ranked_by_weighted_gap_then_id():
    caps = parse(
        HEADER
        + "B-1,Data,small,Initial,Advanced,1\n"        # wg 1
        + "A-2,Data,big,Traditional,Optimal,2\n"       # wg 6
        + "A-1,Data,tie,Traditional,Advanced,1\n"      # wg 2
        + "C-1,Data,tie2,Initial,Optimal,1\n"          # wg 2
        + "Z-9,Data,done,Advanced,Advanced,5\n"        # wg 0, excluded
    )
    ids = [g["capability_id"] for g in ms.score(caps, top=10).top_gaps]
    assert ids == ["A-2", "A-1", "C-1", "B-1"]


def test_top_limit_respected():
    caps = ms.load_worksheet(WORKSHEET)
    assert len(ms.score(caps, top=3).top_gaps) == 3
    assert ms.score(caps, top=0).top_gaps == []


def test_no_gaps_message_in_markdown():
    caps = parse(HEADER + "D-1,Data,a,Optimal,Optimal,1\n")
    assert "No open gaps" in ms.to_markdown(ms.score(caps))


# --- sample worksheet + CLI ----------------------------------------------

def test_sample_worksheet_scores_in_range():
    report = ms.score(ms.load_worksheet(WORKSHEET))
    assert 1 <= report.overall_mean_stage <= 4
    assert 0 <= report.overall_maturity_index <= 100
    assert {p.pillar for p in report.pillars} == set(ms.PILLARS)


def test_cli_markdown(capsys):
    assert ms.main([str(WORKSHEET)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("# Zero Trust Maturity Summary")
    assert "| Identity |" in out


def test_cli_json(capsys):
    assert ms.main([str(WORKSHEET), "--format", "json", "--top", "2"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert set(data) == {"overall_mean_stage", "overall_maturity_index", "pillars", "top_gaps"}
    assert len(data["top_gaps"]) == 2


def test_cli_bad_file_returns_error(tmp_path, capsys):
    bad = tmp_path / "bad.csv"
    bad.write_text(HEADER + "X,Nowhere,f,Initial,Advanced,1\n", encoding="utf-8")
    assert ms.main([str(bad)]) == 1
    assert "unknown pillar" in capsys.readouterr().err


def test_cli_missing_file_returns_error(tmp_path, capsys):
    assert ms.main([str(tmp_path / "nope.csv")]) == 1
    assert "error:" in capsys.readouterr().err
