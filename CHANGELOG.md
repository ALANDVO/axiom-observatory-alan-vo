# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## [1.1.0] - 2026-10-17

### Added
- Masked-select-eliminator profiler counter extraction from recompiler traces (#3504): parses `N walks, M values visited, implications, selects` counters emitted by `MaskedSelectEliminator`.
- Walk-complexity score and risk tier (`none`/`elevated`/`high`/`critical`) persisted per triage session, with an explanatory `PROFILER_WALK_ANALYZED` audit event for runaway walks.
- `walk_complexity_score` and `complexity_risk` surfaced in the session list, session detail and JSON export; aggregate counts in `/api/stats`.
- React dashboard "Walk Complexity" column and detail "Masked-Select Walk Profiler" card with a complexity progress bar.
- `test_profiler.py` unit tests and end-to-end HTTP integration test for counter parsing, scoring thresholds and API flow.

### Changed
- Bumped version to 1.1.0 (minor update).

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-12

### Added
- Initial release of Axiom Observatory (`axiom-observatory-alan-vo`).
- Binary import audit engine mapping PlayStation NID symbols against standard POSIX / libkernel / libSce APIs.
- ML-driven stop classifier predicting failure root causes (missing imports, CFG merge explosions, ancillary VGPR hazards, hardware gaps).
- Persistent SQLite storage for triage records, audit logs, and search queries.
- FastAPI backend with paginated endpoints and JSON export capabilities.
- React + TypeScript dashboard with live analytics, submission workflows, and stop diagnostics.
- Offline reproducible evaluation benchmark comparing rule heuristics against ML classification.
