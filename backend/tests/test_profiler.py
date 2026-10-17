"""Tests for masked-select-eliminator profiler counter extraction (#3504)."""
from app.services.profiler import (
    extract_profiler_counters,
    compute_walk_complexity,
)

# The exact trace shape from TRAINING_DATASET (#3504, Stray stop).
STRAY_TRACE = (
    "masked-lane walk implication loop: 56,190 walks, "
    "1,233 M values visited, selects eliminated"
)


def test_extract_counters_from_stray_trace():
    counters = extract_profiler_counters(STRAY_TRACE)
    assert counters["walks"] == 56190.0
    assert counters["values_visited"] == 56190.0 * 0 + 1_233_000_000.0
    # "selects eliminated" has no number -> not fabricated.
    assert counters["selects_removed"] is None


def test_extract_counters_units_and_decimals():
    trace = "MaskedSelectEliminator: 4,616 selects removed, 210.9 M implications computed"
    counters = extract_profiler_counters(trace)
    assert counters["selects_removed"] == 4616.0
    assert counters["implications"] == 210_900_000.0


def test_extract_counters_missing_returns_none():
    counters = extract_profiler_counters("CFG shared merge splitting exceeded budget")
    assert all(v is None for v in counters.values())


def test_extract_counters_no_number_not_fabricated():
    # Numberless forms must stay None rather than being guessed.
    counters = extract_profiler_counters("selects eliminated without counts")
    assert counters["selects_removed"] is None


def test_complexity_empty_trace_is_none():
    result = compute_walk_complexity({"walks": None, "values_visited": None,
                                      "implications": None, "selects_removed": None})
    assert result["risk"] == "none"
    assert result["score"] == 0.0
    assert result["walks"] == 0


def test_complexity_stray_is_critical():
    counters = extract_profiler_counters(STRAY_TRACE)
    result = compute_walk_complexity(counters)
    assert result["risk"] == "critical"
    assert result["score"] >= 0.85
    assert result["walks"] == 56190
    assert result["values_visited"] == 1_233_000_000
    assert result["signals"]


def test_complexity_small_walk_is_elevated_or_lower():
    counters = extract_profiler_counters("1,000 walks, 1000 values visited")
    result = compute_walk_complexity(counters)
    assert result["risk"] in ("elevated", "none")
    assert 0.0 <= result["score"] <= 1.0


def test_complexity_no_counters_is_none():
    counters = extract_profiler_counters("no profiler counters here")
    result = compute_walk_complexity(counters)
    assert result["risk"] == "none"
    assert result["score"] == 0.0