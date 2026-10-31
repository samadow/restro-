# RESTORA NEXUS — Progress Tracker

| Phase | Name | Status | Date |
|---|---|---|---|
| 0 | Complete project audit (read-only) | ✅ Completed | 2026-10-31 |
| 1 | Backend security & integrity hardening | ⏸ Awaiting approval | — |
| 2 | Backend enablers for frontend | ⬜ Not started | — |
| 3 | Frontend foundation & design system | ⬜ Not started | — |
| 4 | Customer experience | ⬜ Not started | — |
| 5 | Restaurant dashboard | ⬜ Not started | — |
| 6 | Kitchen display & realtime | ⬜ Not started | — |
| 7 | Super admin panel | ⬜ Not started | — |
| 8 | Payments & notifications | ⬜ Not started | — |
| 9 | Production readiness | ⬜ Not started | — |

**Current phase:** 0 completed — stopped, waiting for explicit approval to start Phase 1.

---

## Phase 0 — summary

Done:
- Inspected every non-venv file (backend, config, Docker, nginx, docs, tests, migrations).
- `manage.py check` clean · no pending migrations · 33/33 tests pass · OpenAPI schema valid (0 warnings).
- Reproduced vulnerabilities with a throwaway-test-database probe script (kept outside the project, in the session scratchpad).
- Created: `RESTORA_PROJECT_AUDIT.md`, `RESTORA_API_MAP.md`, `RESTORA_IMPLEMENTATION_PLAN.md`, `RESTORA_PROGRESS.md`.
- No existing source, model, migration, URL, setting or dependency was modified.

Key facts:
- Backend only (Django 6.1.2, DRF 3.18.3, SimpleJWT 5.5.1, drf-spectacular 0.30.0). **No frontend exists.**
- ~40 models, ~150 routes (with legacy aliases), 5 AI endpoints (Groq).

## Discovered problems (open)

| ID | Severity | Problem | Status |
|---|---|---|---|
| P-01 | Critical | Real-format Groq API key in `.env.example` (not gitignored) | Open — **rotate key now** |
| P-02 | Critical | Customer sets order `discount` (create & PATCH) | Open (verified) |
| P-03 | Critical | Customer sets order-item `price` | Open (verified) |
| P-04 | Critical | Negative / arbitrary `delivery_price` | Open (verified) |
| P-05 | High | Product from another restaurant can be ordered | Open (verified) |
| P-06 | High | `PATCH /api/auth/me/` stores password in plaintext | Open (verified) |
| P-07 | High | `change-password` without `new_password` locks the account; no password validators | Open (verified) |
| P-08 | High | Cross-restaurant `assign-table` | Open (verified) |
| P-09 | High | Order with another user's reservation | Open (verified) |
| P-10 | High | Filial can be moved into a foreign restaurant | Open (verified) |
| P-11 | High | Any owner/manager deletes any restaurant's review | Open (verified) |
| P-12 | High | Owner's global role overwritten to customer/staff by `staff_role` | Open (verified) |
| P-13 | Medium | Any order status → any status | Open (verified) |
| P-14 | Medium | Reservations in the past accepted | Open (verified) |
| P-15 | Medium | Unknown admin action deactivates restaurant | Open (verified) |
| P-16 | Medium | FK reassignment not re-validated in several detail views | Open (code review) |
| P-17 | Medium | No row locking on stock / loyalty / payments | Open (code review) |
| P-18 | Medium | No rate limiting on login/register | Open (code review) |
| P-19 | Medium | N+1: 119 queries for 14 order items | Open (measured) |
| P-20 | Medium | No CORS → browser frontend blocked | Open (code review) |
| P-21 | Low | `psycopg`/`gunicorn` in requirements but missing from local venv | Open (verified) |
| P-22 | Low | Inconsistent error envelope between FBVs and exception handler | Open (code review) |
| P-23 | Low | `profil_cr/` unreachable for normal users; duplicated Profile data | Open (code review) |
| P-24 | Low | GET `reports/daily/` writes to DB | Open (code review) |

Not tested in Phase 0: PostgreSQL, Docker/nginx/TLS build, real Groq calls, concurrency, load.

## Next steps

1. **You:** revoke the Groq key at console.groq.com (independent of any phase).
2. **You:** answer the open decisions in `RESTORA_IMPLEMENTATION_PLAN.md` (frontend location/stack, packages, migrations, 3D intensity, payment provider).
3. **You:** approve Phase 1.
4. **Phase 1:** fix P-01…P-18 with regression tests, no API shape changes.
