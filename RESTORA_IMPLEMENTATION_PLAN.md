# RESTORA NEXUS — Implementation Plan

Based on the Phase 0 audit (`RESTORA_PROJECT_AUDIT.md`, `RESTORA_API_MAP.md`). Date: 2026-10-31.

## Guiding principles

1. **Fix money and access bugs before building any UI.** A beautiful frontend on top of a backend where customers can set their own prices is a liability.
2. **Preserve the existing API contract.** No renaming of models/fields/URLs (`Custumer`, `decription`, `kalichestvo`, `dron_stol` stay). New behaviour goes into new endpoints or additive, backward-compatible fields. Legacy URL aliases stay.
3. **Every phase ships with tests.** Each fixed bug gets a regression test; the 33 existing tests must keep passing.
4. **Server is the source of truth for money** (spec §17.4): prices, discounts, delivery fees are computed server-side only.
5. **Premium design must not cost performance or accessibility**: motion respects `prefers-reduced-motion`, 3D is progressive enhancement with a 2D fallback, mobile budget is enforced.
6. One phase at a time; each phase ends with a report and explicit approval.

---

## Phase 1 — Backend security & integrity hardening (no new features)

**Goal:** close every confirmed vulnerability from audit §7 without changing endpoint shapes.

| # | Task | Files | Compatibility note |
|---|---|---|---|
| 1.1 | Rotate the Groq key; replace value in `.env.example` with placeholder | `.env.example` (user rotates key at provider) | — |
| 1.2 | Make `discount` read-only in `OrderSerialiser`; cap stored discount in `Order.calculate_discount` | serializer.py, models.py | field still returned in responses |
| 1.3 | Make `price` read-only in `Bron_productSeria`; always use variant/base price | serializer.py, models.py | field still returned |
| 1.4 | Validate product/variant belong to order's restaurant and variant belongs to product | views.py `AddProduct`, `update_quantity` | new 400 errors only for invalid input |
| 1.5 | `delivery_price` ≥ 0 and server-controlled (read-only for customers; staff may set) | serializer.py, views.py | |
| 1.6 | Validate `reservation` (same user/filial) and `stol` on order create/update; `assign_table` restricted to order's filial; free/occupy tables correctly | views.py | |
| 1.7 | Order status state machine (allowed transitions map); reservation transitions; reject past reservations | views.py / models.py | invalid transitions → 400 |
| 1.8 | `MyProfile.patch`: hash password via `set_password` or drop `password` from update; `change_password` requires & validates `new_password` (`validate_password`); register runs validators | serializer.py, views.py | |
| 1.9 | Re-check tenant ownership when FKs change on update (filial→restaurant, settings, ingredient, supplier, coupon, expense, kitchen, shift, delivery staff) | views.py | |
| 1.10 | `ReviewDetail.perform_destroy` limited to staff of that restaurant | views.py | |
| 1.11 | `staff_role` keeps `owner` for users who own restaurants | views.py | |
| 1.12 | `admin_restaurant_active` accepts only `activate`/`deactivate` (404 otherwise) | views.py | |
| 1.13 | `select_for_update` for loyalty balance, ingredient stock, payments | views.py, models.py | |
| 1.14 | Login/register throttling (`AnonRateThrottle` scope) | settings.py, urls/views | additive |
| 1.15 | Return ingredients to stock when an order sent to kitchen is cancelled; reverse earned points on cancel-after-complete | views.py, models.py | |

**Acceptance:** all 16 probe exploits fail; regression tests added for each; 33 legacy tests pass; `spectacular --validate` clean; no migrations except ones strictly needed (ideally none).
**Effort (estimate):** 2–3 days.

---

## Phase 2 — Backend enablers for a modern frontend

| # | Task | Why |
|---|---|---|
| 2.1 | CORS (`django-cors-headers`, allow-list from env) | browser SPA on another origin is impossible without it |
| 2.2 | Public read endpoints for restaurant/filial discovery (new or relaxed GET), include `is_active`, rating, cover image | customer app landing without login |
| 2.3 | Query optimisation: `select_related`/`prefetch_related` in all list views; lighter list serializers (ids + names) alongside existing nested ones | 119 queries → target ≤ 10 per list |
| 2.4 | Remove-order-item endpoint (new URL) and order-item extras (new model `OrderItemExtra`, additive) | cart UX |
| 2.5 | Enforce `RestaurantSettings` (hours, `delivery_enabled`, `reservation_enabled`) | correctness |
| 2.6 | Image thumbnails / responsive sizes (Pillow-based on upload, WebP) | mobile performance |
| 2.7 | Consistent error envelope for FBV `Response({"error"})` paths | single client error handler |
| 2.8 | i18n foundation: `gettext` for API messages (tg/ru/en via `Accept-Language`); optional translated content fields for menu (additive) | localisation |
| 2.9 | `/api/auth/me/` returns `id, role, fullname, img, restaurants[]` (additive fields) | role-based UI routing |
| 2.10 | Health endpoint, Sentry hook (optional), `CONN_MAX_AGE` | ops |

**Acceptance:** documented in API map; N+1 tests with `assertNumQueries`; schema clean.
**Effort:** 3–5 days.

---

## Phase 3 — Frontend foundation & design system

**Decision needed from you:** location (new `frontend/` folder in this repo vs separate repo) and stack. The spec names **React + TypeScript**; recommended: Vite + React 18 + TypeScript + React Router + TanStack Query + a small CSS-variables design system (Tailwind optional).

| # | Deliverable |
|---|---|
| 3.1 | Project scaffold, lint/format, unit test runner (Vitest), e2e (Playwright) |
| 3.2 | Design tokens: **Obsidian Cinema** (dark) & **Architectural Daylight** (light); type scale, spacing, radii, elevation/depth layers for spatial UI; theme switch respecting `prefers-color-scheme` |
| 3.3 | Motion system: durations/easings tokens, page & shared-element transitions, `prefers-reduced-motion` fallbacks |
| 3.4 | i18n (tg / ru / en) with locale switcher, number/currency (TJS) and date formatting |
| 3.5 | API client: JWT storage strategy, silent refresh, logout/blacklist, unified error handling, pagination helpers |
| 3.6 | Role-aware routing shell: Customer · Restaurant dashboard · Kitchen display · Courier · Super admin |
| 3.7 | Core components: buttons, inputs, selects, date/time pickers, modals/sheets, toasts, tables, cards, skeletons, empty/error states — all keyboard & screen-reader accessible |
| 3.8 | 3D strategy spike: Three.js / React-Three-Fiber limited to hero & restaurant showcase, lazy-loaded, 2D fallback, mobile GPU budget |

**Acceptance:** Lighthouse mobile ≥ 90 performance / 100 accessibility on shell; both themes & 3 languages switchable.
**Effort:** 1–1.5 weeks.

---

## Phase 4 — Customer experience ("Cinematic Gastronomy")

Pages: landing & restaurant discovery · restaurant page (filials, rating, reviews) · menu with categories, variants, extras · cart & checkout (server totals only) · coupon & loyalty points · table availability & reservation · order tracking (polling until Phase 6) · delivery address flow · profile, addresses, favorites, order history · reviews · AI menu assistant chat.
**Depends on:** Phases 1–3. **Effort:** 2 weeks.

## Phase 5 — Restaurant dashboard (owner / manager / waiter / cashier)

Dashboard KPIs (reports endpoints) · restaurants, filials, settings · tables (and later floor plan) · menu CMS with AI descriptions · orders board, assign table/customer, status, send to kitchen · reservations calendar · payments & refunds (cashier mode) · staff, shifts, attendance · inventory, suppliers, recipes, stock movements, AI forecast · expenses & reports · coupons · subscription & plan usage · restaurant notifications · audit log.
**Effort:** 2–3 weeks.

## Phase 6 — Kitchen display & realtime

Backend: Django Channels + Redis (spec Phase 3.7) or SSE for order/kitchen/delivery events. Frontend: full-screen KDS (new / preparing / ready lanes, timers, per-item ready), courier mobile view, live order tracking for customers.
**Effort:** 1–1.5 weeks.

## Phase 7 — Super admin panel

Restaurants activate/deactivate, platform stats, plans CRUD, subscriptions & payments (new admin APIs), users, audit logs.
**Effort:** 1 week.

## Phase 8 — Payments & notifications

Real payment provider (provider to be chosen by you), webhook endpoint, idempotency keys, subscription billing; push / SMS / email notifications; background jobs (Celery) for AI, notifications, daily reports.
**Effort:** 1–2 weeks, depends on provider.

## Phase 9 — Production readiness

Load testing, DB indexes review, caching, nginx gzip/brotli & cache headers, CDN for media, monitoring/error tracking, backup restore drill, security review (OWASP API Top 10), accessibility audit (WCAG 2.2 AA), mobile performance pass.
**Effort:** 1 week.

---

## Recommended order & dependencies

```
Phase 1 (security) ──► Phase 2 (backend enablers) ──► Phase 3 (frontend foundation)
                                                         ├─► Phase 4 (customer)
                                                         ├─► Phase 5 (dashboard)
                                    Phase 6 (realtime) ◄─┤
                                                         └─► Phase 7 (super admin)
Phase 8 (payments/notifications) after 4–5 · Phase 9 last
```

## Open decisions for the product owner

1. Frontend location and stack confirmation (spec: React + TypeScript).
2. Allowed to add packages in Phase 2 (`django-cors-headers`, later `channels`, `redis`, `celery`)?
3. Is a migration acceptable for additive models/fields (order-item extras, translations, thumbnails)?
4. Intensity of 3D (hero-only vs throughout) and target low-end devices.
5. Payment provider for Tajikistan.
6. Should global `role` be replaced by per-restaurant membership later (bigger refactor; Phase 1 only patches the owner overwrite)?
