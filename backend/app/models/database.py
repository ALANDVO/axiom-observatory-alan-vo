from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from app.core.config import settings

Base = declarative_base()

def get_engine(db_url: str = settings.database_url):
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    return create_engine(db_url, connect_args=connect_args)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TriageSession(Base):
    __tablename__ = "triage_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title_id = Column(String(32), index=True, nullable=False)
    title_name = Column(String(128), nullable=False)
    target_os = Column(String(32), default="linux", nullable=False)
    category = Column(String(64), nullable=False)
    confidence = Column(Float, default=0.0)
    root_cause = Column(Text, nullable=False)
    mitigation = Column(Text, nullable=False)
    raw_trace = Column(Text, nullable=False)
    total_imports = Column(Integer, default=0)
    absent_imports = Column(Integer, default=0)
    stub_imports = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    # Masked-select-eliminator profiler counters (#3504), stored as JSON text.
    profiler_counters = Column(Text, default="{}", nullable=False)
    walk_complexity_score = Column(Float, default=0.0, nullable=False)
    complexity_risk = Column(String(32), default="none", nullable=False)

    symbols = relationship("SymbolRecord", back_populates="session", cascade="all, delete-orphan")
    audit_events = relationship("AuditLog", back_populates="session", cascade="all, delete-orphan")

class SymbolRecord(Base):
    __tablename__ = "symbol_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("triage_sessions.id"), nullable=False, index=True)
    nid = Column(String(64), index=True, nullable=False)
    library = Column(String(64), nullable=False)
    function_name = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False)
    caller_module = Column(String(128), default="eboot.bin")

    session = relationship("TriageSession", back_populates="symbols")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("triage_sessions.id"), nullable=True, index=True)
    action = Column(String(64), nullable=False)
    detail = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("TriageSession", back_populates="audit_events")

def init_db():
    Base.metadata.create_all(bind=engine)
