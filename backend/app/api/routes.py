from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import (
    TriageCreateRequest,
    TriageSessionDetail,
    PaginatedTriageResponse,
    StatsResponse,
    NIDLookupResponse,
    MLEvaluationResponse
)
from app.services import triage_service
from app.services.nid_database import lookup_by_nid, lookup_by_name
from app.services.ml_classifier import classifier

router = APIRouter(prefix="/api")

@router.get("/health")
def health():
    return {"status": "ok", "service": "axiom-observatory", "version": "1.0.0"}

@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    return triage_service.get_stats(db)

@router.post("/triage", response_model=TriageSessionDetail)
def create_triage(request: TriageCreateRequest, db: Session = Depends(get_db)):
    return triage_service.perform_triage(db, request)

@router.get("/triage", response_model=PaginatedTriageResponse)
def list_triage(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    items, total = triage_service.list_sessions(
        db, page=page, page_size=page_size, category=category, title_search=search
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/triage/{session_id}", response_model=TriageSessionDetail)
def get_triage(session_id: int, db: Session = Depends(get_db)):
    session = triage_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Triage session not found")
    return session

@router.get("/triage/{session_id}/export")
def export_triage(session_id: int, db: Session = Depends(get_db)):
    session = triage_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Triage session not found")
    return {
        "export_version": "1.0.0",
        "session": {
            "id": session.id,
            "title_id": session.title_id,
            "title_name": session.title_name,
            "target_os": session.target_os,
            "category": session.category,
            "confidence": session.confidence,
            "root_cause": session.root_cause,
            "mitigation": session.mitigation,
            "created_at": session.created_at.isoformat(),
            "symbols": [
                {
                    "nid": s.nid,
                    "library": s.library,
                    "name": s.function_name,
                    "status": s.status,
                    "caller": s.caller_module
                }
                for s in session.symbols
            ],
            "audit_trail": [
                {"action": a.action, "detail": a.detail, "timestamp": a.created_at.isoformat()}
                for a in session.audit_events
            ]
        }
    }

@router.get("/nid/lookup", response_model=NIDLookupResponse)
def lookup_nid(nid: Optional[str] = Query(None), name: Optional[str] = Query(None)):
    if nid:
        info = lookup_by_nid(nid)
        if not info:
            raise HTTPException(status_code=404, detail=f"NID {nid} not found in catalog")
        return {
            "nid": nid,
            "library": info["library"],
            "function_name": info["name"],
            "status": info["status"],
            "notes": info["notes"]
        }
    elif name:
        res = lookup_by_name(name)
        if not res:
            raise HTTPException(status_code=404, detail=f"Function {name} not found in catalog")
        found_nid, info = res
        return {
            "nid": found_nid,
            "library": info["library"],
            "function_name": info["name"],
            "status": info["status"],
            "notes": info["notes"]
        }
    raise HTTPException(status_code=400, detail="Provide either nid or name parameter")

@router.post("/ml/evaluate", response_model=MLEvaluationResponse)
def evaluate_ml():
    return classifier.evaluate()
