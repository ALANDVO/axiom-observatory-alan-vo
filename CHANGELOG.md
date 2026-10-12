# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

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
