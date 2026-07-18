# Friday Vision-First Dependency Audit

Status: Sprint Friday Reset V1.0

## Reviewed Files

- `requirements.txt`
- `frontend/package.json`
- `frontend/package-lock.json`

## Preserved Dependencies

No dependency was removed in this Sprint.

Reason:

- The repository has a large uncommitted broker-research surface.
- Removing packages before archiving tests and tools would make the cleanup harder to verify.
- FastAPI, Pydantic, Pytest, React, Vite, TailwindCSS and chart/UI packages are still used by current code or historical tests.

## Candidate Broker-Era Dependencies For Later Review

| Dependency area | Reason to review later |
| --- | --- |
| CDP/browser control helpers | Broker observation is no longer part of runtime. |
| Socket/WebSocket helpers | Broker realtime ingestion is retired from the product direction. |
| Chart-specific packages | `RealCandleChart` is no longer a primary product surface, but may remain useful for archived demos. |
| IQ Option isolated worker dependencies | Broker provider is retired from runtime. |

## Decision

Dependencies are preserved for this Sprint and marked for a follow-up cleanup after broker code and tests are physically archived.
