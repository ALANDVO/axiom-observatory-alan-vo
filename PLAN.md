# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

shader-cfg-complexity-analyzer

## Roadmap

### binary-import-audit-and-stop-triage — Binary Import Audit and ML Stop Triage

Status: done

Acceptance:
- Ingest ELF/PRX import tables and runtime recompiler log traces
- Resolve known and unknown NIDs using the embedded POSIX/PS5 aerolib catalog
- Classify execution stops into risk categories using a trained ML stop classifier
- Persist triage sessions in SQLite with pagination, filtering, and JSON export
- Interactive React dashboard with summary statistics, submission form, and detail view

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/models/database.py`, `backend/app/models/schemas.py`, `backend/app/services/nid_database.py`, `backend/app/services/ml_classifier.py`, `backend/app/services/triage_service.py`, `backend/app/api/routes.py`, `frontend/src/App.tsx`, `frontend/src/api/client.ts`, `frontend/src/components/Dashboard.tsx`, `frontend/src/components/TriageForm.tsx`, `frontend/src/components/TriageDetail.tsx`

Tests: `backend/tests/test_triage_api.py`, `backend/tests/test_ml_classifier.py`, `backend/tests/test_nid_database.py`, `frontend/src/test/App.test.tsx`

### shader-cfg-complexity-analyzer — Shader CFG Complexity and Masked-Lane Walk Bottleneck Detector

Status: done

Acceptance:
- Parse masked-select-eliminator profiler counters (walks, values_visited, implications, selects_removed) from recompiler traces
- Compute a walk-complexity score and advisory risk tier grounded in #3504
- Persist counters/score/risk per triage session and surface in dashboard, detail, and JSON export
- Aggregate complexity risk counts in /api/stats

Implementation: `backend/app/services/profiler.py`, `backend/app/models/database.py`, `backend/app/models/schemas.py`, `backend/app/services/triage_service.py`, `backend/app/api/routes.py`, `frontend/src/api/client.ts`, `frontend/src/components/Dashboard.tsx`, `frontend/src/components/TriageDetail.tsx`

Tests: `backend/tests/test_profiler.py`, `backend/tests/test_triage_api.py`, `frontend/src/test/App.test.tsx`

### execution-bisection-tracker — Multi-Stage Execution Stop Sequence and Bisection Tracker

Status: planned

Acceptance:
- Track linear progression through multiple startup stops (stops 1..N)
- Correlate shader-cache miss thresholds with crash points
- Automated commit bisection replay simulation for recompiler regressions

### oidc-keycloak-auth-integration — OIDC Keycloak Authentication with SAML Broker Support

Status: planned

Acceptance:
- Full PKCE authorization-code flow with Keycloak
- Role-based access control for viewer, analyst, and admin
- Local demo mode toggle for unauthenticated localhost testing

