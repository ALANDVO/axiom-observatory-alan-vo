from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class SymbolItem(BaseModel):
    nid: str
    library: str
    function_name: str
    status: str  # implemented, stub, absent
    caller_module: Optional[str] = "eboot.bin"

class TriageCreateRequest(BaseModel):
    title_id: str = Field(..., min_length=4, max_length=32, json_schema_extra={"example": "PPSA11386"})
    title_name: str = Field(..., min_length=2, max_length=128, json_schema_extra={"example": "007 First Light"})
    target_os: str = Field(default="linux", json_schema_extra={"example": "linux"})
    raw_trace: str = Field(..., min_length=5, json_schema_extra={"example": "loader: undefined symbol: qOn+wm28wmA (sceSslGetCaList)"})

class SymbolResponse(BaseModel):
    id: int
    nid: str
    library: str
    function_name: str
    status: str
    caller_module: str

    model_config = {"from_attributes": True}

class AuditResponse(BaseModel):
    id: int
    action: str
    detail: str
    created_at: datetime

    model_config = {"from_attributes": True}

class TriageSessionSummary(BaseModel):
    id: int
    title_id: str
    title_name: str
    target_os: str
    category: str
    confidence: float
    total_imports: int
    absent_imports: int
    stub_imports: int
    created_at: datetime

    model_config = {"from_attributes": True}

class TriageSessionDetail(BaseModel):
    id: int
    title_id: str
    title_name: str
    target_os: str
    category: str
    confidence: float
    root_cause: str
    mitigation: str
    raw_trace: str
    total_imports: int
    absent_imports: int
    stub_imports: int
    created_at: datetime
    symbols: List[SymbolResponse] = []
    audit_events: List[AuditResponse] = []

    model_config = {"from_attributes": True}

class PaginatedTriageResponse(BaseModel):
    items: List[TriageSessionSummary]
    total: int
    page: int
    page_size: int

class StatsResponse(BaseModel):
    total_sessions: int
    total_symbols_analyzed: int
    total_absent_symbols: int
    category_counts: dict
    target_os_counts: dict

class NIDLookupResponse(BaseModel):
    nid: str
    library: str
    function_name: str
    status: str
    notes: str

class MLEvaluationResponse(BaseModel):
    total_samples: int
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    classes: List[str]
    sample_predictions: List[dict]
