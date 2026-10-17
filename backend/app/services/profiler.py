"""Structured extraction of masked-select-eliminator profiler counters from
recompiler traces, with a runaway-walk complexity assessment.

Grounded in AnyPS5 issue #3504 ("Shader preparation: masked-lane walk takes
150 to 400 s"): recompiler traces such as::

    masked-lane walk implication loop: 56,190 walks, 1,233 M values visited, selects eliminated

carry the diagnostic counters that distinguish a benign optimization walk from
a pathological one. The issue's measured Stray stop (~56.2k walks, ~1.2 billion
values visited, ~211M implications, ~4.6k selects removed) motivates the
runaway thresholds below.

These signals are advisory only; they summarize what the recompiler logged,
never fabricating counters the trace did not expose.
"""
from __future__ import annotations

import re
from math import log10
from typing import Dict, List, Optional

# Magnitude multipliers for the human-readable units the recompiler emits.
_UNITS: Dict[str, float] = {"K": 1_000.0, "M": 1_000_000.0, "G": 1_000_000_000.0}

# Reference point for normalization -- the pathological Stray stop from #3504.
_REF_WALKS = 56_000.0
_REF_DEPTH = 22_000.0


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _number_with_unit(pattern: str, text: str) -> Optional[float]:
    """Match ``<num>[,<num>]+ [unit]?`` against *text* and return a float.

    *num* may carry comma grouping (``56,190``) and a decimal part
    (``210.9``). An optional trailing unit token (``K``/``M``/``G``) scales it.
    Returns ``None`` when the pattern is absent -- counters are never guessed.
    """
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    num_str = match.group("num").replace(",", "")
    try:
        value = float(num_str)
    except ValueError:
        return None
    unit = match.groupdict().get("unit")
    if unit:
        value *= _UNITS.get(unit.upper(), 1.0)
    return value


# `56,190 walks` (optionally `1.5 K walks`).
_WALKS_RE = r"(?P<num>[\d,]+)(?:\.\d+)?(?:\s+(?P<unit>[KMGkmg]))?\s+walks"
# `1,233 M values visited` or `1500 values visited`.
_VALUES_RE = r"(?P<num>[\d,]+(?:\.\d+)?)(?:\s+(?P<unit>[KMGkmg]))?\s+values?\s+visited"
# `210.9 M implications computed`.
_IMPLICATIONS_RE = r"(?P<num>[\d,]+(?:\.\d+)?)(?:\s+(?P<unit>[KMGkmg]))?\s+implications?"
# `4,616 selects removed` / `selects eliminated` (numberless).
_SELECTS_RE = r"(?P<num>[\d,]+)\s+selects?\s+(?:removed|eliminated|optimized)"


def extract_profiler_counters(trace_text: str) -> Dict[str, Optional[float]]:
    """Pull masked-select-eliminator counters out of a recompiler trace.

    Returns a dict with keys ``walks``, ``values_visited``,
    ``implications`` and ``selects_removed``; each maps to a float or
    ``None`` when the trace did not expose that counter.
    """
    return {
        "walks": _number_with_unit(_WALKS_RE, trace_text),
        "values_visited": _number_with_unit(_VALUES_RE, trace_text),
        "implications": _number_with_unit(_IMPLICATIONS_RE, trace_text),
        "selects_removed": _number_with_unit(_SELECTS_RE, trace_text),
    }


def _any_counters(counters: Dict[str, Optional[float]]) -> bool:
    return any(v is not None for v in counters.values())


def compute_walk_complexity(counters: Dict[str, Optional[float]]) -> Dict[str, object]:
    """Assess whether a masked-lane walk is runaway and needs a per-program budget.

    The score normalizes each dimension to the #3504 Stray reference (both
    reach ~1.0 there) and the risk tier is derived from it:

    * ``none``     -- no profiler counters present in the trace
    * ``elevated`` -- small but nonzero walk volume
    * ``high``     -- deep traversal; implication de-duplication needed
    * ``critical`` -- Stray-scale; exceeds the recommended per-program budget

    Advisory only; thresholds are grounded in #3504's measured stop.
    """
    walks = counters.get("walks")
    values = counters.get("values_visited")

    if not _any_counters(counters):
        return {
            "score": 0.0,
            "risk": "none",
            "walks": 0,
            "values_visited": 0,
            "depth": 0.0,
            "signals": ["no masked-lane walk counters present in trace"],
        }

    walk_count = float(walks) if walks else 0.0
    value_count = float(values) if values else 0.0
    depth = (value_count / walk_count) if walk_count > 0 else 0.0

    vol = min(1.0, log10(max(walk_count, 1.0)) / log10(_REF_WALKS))
    dep = min(1.0, log10(max(depth, 1.0)) / log10(_REF_DEPTH)) if depth > 0 else 0.0
    score = round(_clamp(_clamp(vol, 0.0, 1.0) * 0.4 + _clamp(dep, 0.0, 1.0) * 0.6, 0.0, 1.0), 4)

    if score >= 0.85:
        risk = "critical"
    elif score >= 0.55:
        risk = "high"
    elif score >= 0.25:
        risk = "elevated"
    else:
        risk = "none"

    signals: List[str] = []
    if walk_count > 0:
        signals.append(
            f"{int(walk_count):,} masked-lane walks, {int(value_count):,} values visited"
        )
    if values is not None and walk_count > 0:
        signals.append(f"average ~{int(depth):,} values traversed per walk")
    if risk == "critical":
        signals.append("exceeds per-program walk budget (#3504); enable masked-select visitor capping")
    elif risk == "high":
        signals.append("deep traversal; consider per-mask implication de-duplication (#3504)")
    elif risk == "elevated":
        signals.append("nonzero walk volume; monitor for regression in walk depth")
    if not signals:
        signals.append("profiler counters present but below runaway thresholds")

    return {
        "score": score,
        "risk": risk,
        "walks": int(walk_count) if walk_count else 0,
        "values_visited": int(value_count) if value_count else 0,
        "depth": round(depth, 2),
        "signals": signals,
    }