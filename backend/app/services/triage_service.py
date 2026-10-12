from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import TriageSession, SymbolRecord, AuditLog
from app.models.schemas import TriageCreateRequest
from app.services.nid_database import extract_symbols_from_trace
from app.services.ml_classifier import classifier

def perform_triage(db: Session, request: TriageCreateRequest) -> TriageSession:
    # 1. Parse symbol dependencies from trace
    extracted = extract_symbols_from_trace(request.raw_trace)

    # 2. ML Prediction on execution stop
    prediction = classifier.predict(request.raw_trace)

    total_imports = len(extracted)
    absent_imports = sum(1 for s in extracted if s["status"] == "absent")
    stub_imports = sum(1 for s in extracted if s["status"] == "stub")

    # 3. Create Session Record
    session = TriageSession(
        title_id=request.title_id.strip().upper(),
        title_name=request.title_name.strip(),
        target_os=request.target_os.strip().lower(),
        category=prediction["category"],
        confidence=prediction["confidence"],
        root_cause=prediction["root_cause"],
        mitigation=prediction["mitigation"],
        raw_trace=request.raw_trace.strip(),
        total_imports=total_imports,
        absent_imports=absent_imports,
        stub_imports=stub_imports
    )
    db.add(session)
    db.flush()

    # 4. Create Symbol Records
    for sym in extracted:
        sym_rec = SymbolRecord(
            session_id=session.id,
            nid=sym["nid"],
            library=sym["library"],
            function_name=sym["function_name"],
            status=sym["status"],
            caller_module=sym.get("caller_module", "eboot.bin")
        )
        db.add(sym_rec)

    # 5. Audit Log Event
    audit = AuditLog(
        session_id=session.id,
        action="TRIAGE_ANALYZED",
        detail=f"Analyzed {request.title_id} ({request.title_name}) on {request.target_os}: classified as {prediction['category']} with {confidence_percent(prediction['confidence'])} confidence. Found {total_imports} symbols ({absent_imports} absent)."
    )
    db.add(audit)

    db.commit()
    db.refresh(session)
    return session

def confidence_percent(val: float) -> str:
    return f"{round(val * 100, 1)}%"

def get_session(db: Session, session_id: int) -> Optional[TriageSession]:
    return db.query(TriageSession).filter(TriageSession.id == session_id).first()

def list_sessions(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    title_search: Optional[str] = None
) -> Tuple[List[TriageSession], int]:
    query = db.query(TriageSession)

    if category:
        query = query.filter(TriageSession.category == category)
    if title_search:
        search_pattern = f"%{title_search}%"
        query = query.filter(
            (TriageSession.title_id.ilike(search_pattern)) |
            (TriageSession.title_name.ilike(search_pattern))
        )

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(TriageSession.created_at.desc()).offset(offset).limit(page_size).all()
    return items, total

def get_stats(db: Session) -> Dict[str, Any]:
    total_sessions = db.query(TriageSession).count()
    total_symbols = db.query(SymbolRecord).count()
    total_absent = db.query(SymbolRecord).filter(SymbolRecord.status == "absent").count()

    cat_counts = {}
    for cat, count in db.query(TriageSession.category, func.count(TriageSession.id)).group_by(TriageSession.category).all():
        cat_counts[cat] = count

    os_counts = {}
    for os_name, count in db.query(TriageSession.target_os, func.count(TriageSession.id)).group_by(TriageSession.target_os).all():
        os_counts[os_name] = count

    return {
        "total_sessions": total_sessions,
        "total_symbols_analyzed": total_symbols,
        "total_absent_symbols": total_absent,
        "category_counts": cat_counts,
        "target_os_counts": os_counts
    }
