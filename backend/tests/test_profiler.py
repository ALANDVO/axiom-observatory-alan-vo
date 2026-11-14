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


def test_extract_counters_units_without_spaces():
    # Units like "50K walks" or "1.2G values visited" without space.
    trace = "masked-lane walk: 50K walks, 1.2G values visited, 200M implications, 10 selects removed"
    counters = extract_profiler_counters(trace)
    assert counters["walks"] == 50_000.0
    assert counters["values_visited"] == 1_200_000_000.0
    assert counters["implications"] == 200_000_000.0
    assert counters["selects_removed"] == 10.0


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
def test_extract_counters_selects_passive_voice():
    # Passive voice forms should be parsed.
    trace = "500 selects were eliminated during optimization"
    counters = extract_profiler_counters(trace)
    assert counters["selects_removed"] == 500.0


def test_extract_counters_selects_got_removed():
    # "got removed" colloquial form.
    trace = "1,234 selects got removed from the CFG"
    counters = extract_profiler_counters(trace)
    assert counters["selects_removed"] == 1234.0


def test_extract_counters_selects_with_colon():
    # Colon-separated format.
    trace = "selects eliminated: 1,234"
    counters = extract_profiler_counters(trace)
    assert counters["selects_removed"] == 1234.0


def test_extract_counters_selects_removed_colon():
    # Colon after verb.
    trace = "selects removed: 500"
    counters = extract_profiler_counters(trace)
    assert counters["selects_removed"] == 500.0


def test_extract_counters_eliminated_colon():
    # Colon after verb before selects.
    trace = "eliminated: 500 selects"
    counters = extract_profiler_counters(trace)
    assert counters["selects_removed"] == 500.0


def test_extract_counters_optimized_colon():
    # Colon with optimized.
    trace = "selects optimized: 100"
    counters = extract_profiler_counters(trace)
    assert counters["selects_removed"] == 100.0

# Execution bisection tracker tests
def test_update_stop_progression():
    """Test updating stop progression for a triage session.
    
    Verifies that the stop_progression field can be updated
    via the API endpoint, tracking linear progression
    through multiple startup stops (stops 1..N).
    """
    from sqlalchemy.orm import Session
    from app.services.triage_service import perform_triage, update_stop_progression
    from app.models.database import TriageSession, Base, engine
    from app.models.schemas import TriageCreateRequest
    from fastapi.security import OAuth2PasswordBearer
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = Session(engine)
    
    # Create a test triage session
    request = TriageCreateRequest(
        title_id="TEST0001",
        title_name="Test Title",
        target_os="linux",
        raw_trace="masked-lane walk implication loop: 1000 walks, 500 values visited, selects eliminated"
    )
    session = perform_triage(db, request)
    
    # Test updating stop progression
    updated = update_stop_progression(db, session.id, [1, 2, 3])
    assert updated is not None
    assert updated.stop_progression == [1, 2, 3]
    
    # Test updating with new stops (appending)
    updated2 = update_stop_progression(db, session.id, [1, 2, 3, 4, 5])
    assert updated2 is not None
    assert updated2.stop_progression == [1, 2, 3, 4, 5]
    
    # Test with non-existent session
    none_updated = update_stop_progression(db, 9999, [1, 2, 3])
    assert none_updated is None
    
    db.close()

def test_stop_progression_empty():
    """Test that empty stop progression list is handled correctly."""
    from sqlalchemy.orm import Session
    from app.services.triage_service import perform_triage, update_stop_progression
    from app.models.database import TriageSession, Base, engine
    from app.models.schemas import TriageCreateRequest
    
    Base.metadata.create_all(bind=engine)
    
    db = Session(engine)
    
    request = TriageCreateRequest(
        title_id="TEST0002",
        title_name="Test Title 2",
        target_os="linux",
        raw_trace="masked-lane walk implication loop: 500 walks, 250 values visited, selects eliminated"
    )
    session = perform_triage(db, request)
    
    # Test with empty list
    updated = update_stop_progression(db, session.id, [])
    assert updated is not None
    assert updated.stop_progression == []
    
    db.close()

# Execution bisection tracker tests
def test_update_stop_progression():
    """Test updating stop progression for a triage session.
    
    Verifies that the stop_progression field can be updated
    via the API endpoint, tracking linear progression
    through multiple startup stops (stops 1..N).
    """
    from sqlalchemy.orm import Session
    from app.services.triage_service import perform_triage, update_stop_progression
    from app.models.database import TriageSession, Base, engine
    from app.models.schemas import TriageCreateRequest
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = Session(engine)
    
    # Create a test triage session
    request = TriageCreateRequest(
        title_id="TEST0001",
        title_name="Test Title",
        target_os="linux",
        raw_trace="masked-lane walk implication loop: 1000 walks, 500 values visited, selects eliminated"
    )
    session = perform_triage(db, request)
    
    # Test updating stop progression
    updated = update_stop_progression(db, session.id, [1, 2, 3])
    assert updated is not None
    assert updated.stop_progression == [1, 2, 3]
    
    # Test updating with new stops (appending)
    updated2 = update_stop_progression(db, session.id, [1, 2, 3, 4, 5])
    assert updated2 is not None
    assert updated2.stop_progression == [1, 2, 3, 4, 5]
    
    # Test with non-existent session
    none_updated = update_stop_progression(db, 9999, [1, 2, 3])
    assert none_updated is None
    
    db.close()
def test_stop_progression_empty():
    """Test that empty stop progression list is handled correctly."""
    from sqlalchemy.orm import Session
    from app.services.triage_service import perform_triage, update_stop_progression
    from app.models.database import TriageSession, Base, engine
    from app.models.schemas import TriageCreateRequest
    
    Base.metadata.create_all(bind=engine)
    
    db = Session(engine)
    
    request = TriageCreateRequest(
        title_id="TEST0002",
        title_name="Test Title 2",
        target_os="linux",
        raw_trace="masked-lane walk implication loop: 500 walks, 250 values visited, selects eliminated"
    )
    session = perform_triage(db, request)
    
    # Test with empty list
    updated = update_stop_progression(db, session.id, [])
    assert updated is not None
    assert updated.stop_progression == []
    
    db.close()
