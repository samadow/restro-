# RESTORA — Project Audit (Phase 0)

Audit date: 2026-10-31 · Scope: entire repository at `C:\Users\user\Desktop\restarant` · Mode: read-only

Legend used throughout:
- **[VERIFIED]** — reproduced by running code (Django test client on a throwaway test database) or by a tool (`manage.py check`, `test`, `spectacular --validate`).
- **[CODE]** — established by reading the source; not executed.
- **[ASSUMPTION]** — inference that could not be checked.

---

## 1. Executive summary

- RESTORA is currently a **backend-only** project: a Django 6.1 + Django REST Framework JSON API for a multi-tenant restaurant SaaS. **There is no frontend in the repository** — no HTML templates, JS, CSS, `package.json`, static assets, images or fonts. [VERIFIED by full file listing]
- The backend is feature-rich (≈40 models, ≈150 URL routes) and covers accounts, restaurants/branches, tables, reservations, menu, orders, kitchen, payments/refunds, inventory, staff, customers, reviews, notifications, reports, subscriptions, coupons, loyalty, delivery, audit log, super-admin and 5 AI endpoints.
- Health: `manage.py check` → no issues; `makemigrations --check` → no pending changes; **33/33 tests pass**; OpenAPI schema generates and validates with 0 warnings. [VERIFIED]
- **Several critical money-integrity and access-control bugs were reproduced** (customer can set own price/discount, negative delivery price, cross-tenant writes, plaintext password storage via `/api/auth/me/`). See §7.
- **A live-looking Groq API key is committed in `.env.example`**, a file that is *not* in `.gitignore`. See §7.1.

---

## 2. Repository structure

```
restarant/
├── manage.py
├── requirements.txt            # pinned backend deps
├── Dockerfile                  # python:3.13-slim, gunicorn, non-root user
├── docker-compose.yml          # db (postgres:17) + web + nginx:1.27
├── nginx/nginx.conf            # 80→443 redirect, TLS, /static, /media, proxy to web:8000
├── DEPLOY.md                   # Ubuntu + Docker deploy, cron for subscriptions & pg_dump
├── .env / .env.example         # environment configuration (see §2.4)
├── .gitignore / .dockerignore
├── db.sqlite3                  # local dev database (640 KB)
├── server/                     # Django project
│   ├── settings.py             # env loader, DRF, JWT, spectacular, security, logging
│   ├── urls.py                 # /admin/, /api/schema|docs|redoc/, /swagger/, /api/ → myapp
│   ├── asgi.py / wsgi.py
│   └── readme.md               # Technical specification (ТЗ), Tajik/Russian, 1154 lines
└── myapp/                      # single Django app containing everything
    ├── models.py      (906 lines)   ~40 models + notification/loyalty helpers
    ├── serializer.py  (544 lines)   ~45 serializers
    ├── views.py       (3966 lines)  all API views (generic CBVs + @api_view FBVs)
    ├── urls.py        (188 lines)   all /api/ routes
    ├── permissions.py               role classes + tenant scoping helpers
    ├── middleware.py                AuditLogMiddleware
    ├── exceptions.py                unified error envelope
    ├── pagination.py                PageNumberPagination (20, max 100)
    ├── ai.py                        Groq (OpenAI-compatible) client
    ├── admin.py                     registers every model with default ModelAdmin
    ├── tests.py       (454 lines)   33 API tests
    ├── management/commands/check_subscriptions.py
    └── migrations/ 0001 … 0011
```

Not a git repository (no `.git`). [VERIFIED]

### 2.1 Technology stack

| Layer | Technology | Version | Source |
|---|---|---|---|
| Language | Python | 3.13 | `.venv`, Dockerfile |
| Framework | Django | 6.1.2 | requirements.txt, pip list |
| API | djangorestframework | 3.18.3 | " |
| Auth | djangorestframework-simplejwt (+ token_blacklist app) | 5.5.1 | " |
| API docs | drf-spectacular | 0.30.0 | " |
| Images | Pillow | 13.0.0 | " |
| DB (prod) | PostgreSQL 17 via psycopg[binary] | 3.2.9 | requirements.txt, compose |
| DB (dev) | SQLite | — | settings.py fallback when `DB_NAME` empty |
| App server | gunicorn | 23.0.0 | requirements.txt |
| Proxy | nginx | 1.27 | compose |
| AI | Groq Chat Completions (OpenAI-compatible), model `openai/gpt-oss-120b` | — | ai.py, settings |
| Frontend | **none present** | — | — |

Discrepancy: `psycopg` and `gunicorn` are in `requirements.txt` but **not installed in the local `.venv`** (pip list). Local dev therefore only works with SQLite and `runserver`. [VERIFIED]

The specification (`server/readme.md` §2) lists **django-filter, Redis, Django Channels, Celery** and a **React + TypeScript** frontend; none of these exist in code or dependencies. [VERIFIED]

### 2.2 Routing

- `server/urls.py`: `admin/`, `api/schema/`, `api/docs/` (Swagger UI), `api/redoc/`, `swagger/` (duplicate Swagger), `api/` → `myapp.urls`. Media served by Django only when `DEBUG=True`.
- `myapp/urls.py`: flat list of `path()` entries, no DRF routers/ViewSets. Many endpoints have **legacy aliases** (e.g. `/api/Restarant/<pk>/` = `/api/restaurants/<pk>/`, `/api/productApi/` = `/api/products/`). Full map: `RESTORA_API_MAP.md`.

### 2.3 Static files, assets, fonts

- `STATIC_ROOT=staticfiles/`, `MEDIA_ROOT=media/` — neither directory exists locally. No project images/fonts. Only static content is Django admin + Swagger/ReDoc (served from CDN by drf-spectacular by default [CODE: default `SWAGGER_UI_DIST`]).
- Uploaded images: `ImageField`s on users, restaurants, filials, categories, products (`upload_to=` users/, restaurant/, filial/, category/, product/). No resizing/thumbnails, no size/type validation beyond Pillow; nginx caps body at 10 MB.

### 2.4 Environment configuration

`settings.py` parses `.env` itself (no python-dotenv); real env vars take priority.

| Variable | Default | Notes |
|---|---|---|
| `SECRET_KEY` | — (required, raises if missing) | good |
| `DEBUG` | `False` | good |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | |
| `CSRF_TRUSTED_ORIGINS` | empty | |
| `TIME_ZONE` | `UTC` (`.env.example`: Asia/Dushanbe) | |
| `DB_NAME/USER/PASSWORD/HOST/PORT` | empty → SQLite | |
| `SECURE_SSL_REDIRECT` | `True` when not DEBUG | |
| `LOG_LEVEL` | `INFO` | console logging only |
| `GROQ_API_KEY`, `GROQ_MODEL`, `AI_RATE` | `''`, `openai/gpt-oss-120b`, `30/hour` | |

Production hardening when `DEBUG=False`: proxy SSL header, SSL redirect, secure cookies, HSTS 30 days incl. subdomains, nosniff. **No CORS configuration** (no `django-cors-headers`) — a browser frontend on another origin cannot call the API. [CODE]

### 2.5 Testing setup

- Django `APITestCase`, file `myapp/tests.py`, 33 tests across Auth, Roles, Restaurant, Subscription, Menu, Reservation, Order, Payment, Inventory, Customer data, Delivery, Admin/Audit, AI (Groq mocked). Run: `python manage.py test myapp`. **All pass.** [VERIFIED]
- No coverage tooling, no CI config, no frontend tests (no frontend).
- Gaps: none of the bugs in §7 are covered; no tests for reports, shifts/attendance, notifications endpoints, restaurant settings, coupons validation edge cases, concurrency.

---

## 3. How frontend and backend communicate

There is no frontend yet. The intended contract, derivable from code:

- **Transport:** JSON over HTTPS under `/api/`; multipart/form-data for endpoints with images.
- **Auth:** `Authorization: Bearer <access>` JWT (SimpleJWT). Access 50 min, refresh 1 day, refresh-token blacklist on logout. No rotation, no cookie/session auth for the API (`DEFAULT_AUTHENTICATION_CLASSES` = JWT only).
- **Pagination:** list endpoints return `{count, next, previous, results}`; `?page=` and `?page_size=` (≤100). Exceptions: `reports/expenses/` (custom un-paginated payload) and FBVs.
- **Errors:** unified envelope `{"error": "<first message>", "details": <original DRF errors>, "status_code": N}` for exceptions raised through DRF. Note: many FBVs return `Response({"error": ...}, status=400)` directly — those **lack** `details`/`status_code`, and serializer errors returned manually (`serializer.errors`) are raw DRF format. Frontend must handle both shapes. [CODE]
- **Docs:** live OpenAPI 3 at `/api/schema/`, Swagger UI `/api/docs/`, ReDoc `/api/redoc/`.
- **Realtime:** none (no WebSocket/SSE). Kitchen/order status screens would have to poll.
- **CORS:** not configured — a separate-origin SPA will be blocked by browsers until added.

---

## 4. Backend audit — features as implemented

### 4.1 Users, roles, authentication

- Custom user `Custumer(AbstractUser)` (`AUTH_USER_MODEL='myapp.Custumer'`) with `fullname`, `phon_number`, `img`, **single global `role`** ∈ customer, owner, manager, waiter, chef, cashier, delivery. Plus Django `is_superuser` = platform "Super Admin".
- Separate `Profile` (1:1) duplicating fullname/phone/img/role + `bio`; created automatically on registration.
- Auth: JWT obtain/refresh/logout(blacklist). Registration open to anyone, always role `customer`.
- Role transitions: creating a restaurant → `owner`; `Staff` create/update/delete recomputes role from latest active Staff row (`staff_role`); `DeliveryStaff` create → `delivery`; owner can set any role on users employed in their restaurants (`change_role`).
- **Limitations:**
  - Role is global, not per restaurant. A person cannot be owner of A and waiter in B. `staff_role` overwrites `owner` → **owner loses owner role** after being added/removed as staff anywhere. [VERIFIED]
  - Registration serializer does not run `AUTH_PASSWORD_VALIDATORS`; `change_password` does not validate either and accepts a missing `new_password` → `set_password(None)` → **account becomes unusable**. [VERIFIED]
  - `PATCH /api/auth/me/` with `password` stores it **in plaintext** (default `ModelSerializer.update`), breaking login and leaking the password in DB. [VERIFIED]
  - Registration exposes only `username, phon_number, password` (no email, no fullname).

### 4.2 Permissions & tenant isolation

- Role classes in `permissions.py` (superuser passes all): `IsOwner`(owner), `IsManager`(owner, manager), `IsChef`(+chef), `IsCashier`(+cashier), `IsWaiter`(owner, manager, waiter, cashier), `IsDelivery`(owner, manager, delivery), `IsSuperAdmin`.
- Tenant scoping helpers: `my_restaurants` (owned OR active staff), `my_owned_restaurants`, `my_filials` (filials of owned restaurants OR where user is active staff), `my_orders` (own orders OR orders of my filials), `check_restaurant`, `check_filial`.
- No `DEFAULT_PERMISSION_CLASSES` → DRF default is **AllowAny**; every view sets its own. Public (anonymous) endpoints: register, login/refresh, `menu/`, category/product/variant/extra GET, reviews GET, restaurant rating, subscription plans GET. [VERIFIED for menu, reviews, plans, products]
- Isolation is generally enforced via queryset scoping (tests confirm other owners get 404/0 rows). **Gaps reproduced:** cross-restaurant table assign, foreign product in order, foreign reservation on order, filial moved to another restaurant, foreign review deletion (§7).

### 4.3 Restaurant & branch (filial)

- `Restaurant` (owner, name, description, img required, address, phone, is_active), `filial` (restaurant, name, address, img required, phone, is_active), `RestaurantSettings` (1:1; currency TJS, language ru, opening/closing time, delivery_enabled, reservation_enabled).
- Anyone authenticated can create a restaurant (becomes owner). Filial creation requires owner + **active subscription** + plan limit (`max_filial`).
- **Limitations:** `RestaurantSettings.delivery_enabled/reservation_enabled/opening/closing` are **not enforced** anywhere except `opening_time` used for "late" attendance. `RestarantSSerializers` does not expose `is_active`. Restaurant list requires authentication (customers can't browse anonymously, while menu is public). Filial update lets owner/manager change `restaurant` to any id. [VERIFIED]

### 4.4 Tables (`Stol`)

- Fields: filial, name, description, capacity, status (free/busy/reserved).
- Status set to `busy` when an order with a table is created and to `free` on order completed/cancelled (via `OrderStatusHistory.save`). `reserved` is never set automatically.
- Availability check `GET tables/<pk>/available/` computes time overlap with pending/confirmed reservations (default 2 h slot).
- **Limitations:** waiters can update **and delete** tables (`StolApi` allows waiter for write). No check that a table is not already busy when ordering.

### 4.5 Menu

- `Category` (restaurant, img required), `Product` (category, `decription` [sic], price, img required, is_available, preparation_time), `ProductVariant` (name, price — *replaces* base price), `ProductExtra` (name, price).
- Writes: owner/manager of that restaurant. Reads public. `/api/menu/` returns active categories of active restaurants with available products + active variants/extras.
- **Limitations:** `ProductExtra` **cannot be attached to an order item** (no model link/endpoint) — extras are display-only. `/api/products/` list includes unavailable products and products of inactive restaurants. No ordering/sort fields, no product tags/allergens/images gallery. Menu serializer has N+1 (2 queries per product).

### 4.6 Reservations (`dron_stol` = "bron")

- Fields: user, filial, stol, date, `vakt` (start), end_time, guests, status (pending/confirmed/cancelled/completed/no_show), comment.
- Validations: table belongs to filial, guests ≤ capacity, end > start, no overlap; filial & restaurant active. Notifications on create/status change.
- **Limitations:** past dates accepted [VERIFIED]; opening hours and `reservation_enabled` ignored; any staff of the filial (incl. chef) can edit/delete via detail; customers can hard-DELETE their reservation (bypasses cancel); status transitions unrestricted; table `status` not set to `reserved`.

### 4.7 Orders & order items

- `Order`: user, filial, stol, reservation, order_number (`ORD-000001` auto), order_type (free text, default dine_in; `delivery` set automatically), status (new→confirmed→preparing→ready→served→completed / cancelled), total_price, discount, coupon, points_used, comment.
- `Order.save()` **always** recomputes `total_price` = Σ items + delivery price and `discount` = points×0.50 + coupon (capped at total) — but **if no coupon and no points, the stored/client-supplied `discount` is kept as is, uncapped**.
- `dron_product` (order item): product, variant, product_name snapshot, `kalichestvo` (quantity), price (variant or base unless provided), total_price. Saving/deleting an item re-saves the order.
- `OrderStatusHistory.save()` side effects: customer notification, restaurant notification on cancel, loyalty earn on completed, points return on cancel, free the table.
- **Limitations / bugs:** client can set `discount` (create and PATCH) and item `price`; foreign products allowed; any status → any status (e.g. completed → new) [VERIFIED]; no endpoint to remove an order item (model supports it); `order_number` writable and not unique; `reservation` not validated; ingredients are not returned to stock on cancel after kitchen; `cancel_order` for staff allowed from any non-final status; double `save()` per order save.

### 4.8 Kitchen

- `Kitchen` per filial; `send-to-kitchen` (waiter+) creates `KitchenOrder` + one `KitchenOrderItem` per order item in the **first active kitchen**, checks & deducts ingredients, sets order `preparing`.
- Chef: list queue (excludes ready by default), start (pending→preparing), ready (all items), per-item ready (auto-completes ticket). Ticket ready → order `ready`.
- **Limitations:** items added after sending are never sent; no multi-station routing; no "served" flow from kitchen; no realtime.

### 4.9 Payments & refunds

- `Payment` (order, user, amount, method cash/card/online, status, transaction_id). Staff (owner/manager/cashier) record any method; customers may only pay own order **online**. Amount defaults to remaining; overpay rejected. **Online is a mock**: instantly `paid` with `MOCK-xxxx` id — no gateway.
- `Refund` by manager+: partial/full, payment status → partially_refunded/refunded.
- `order_payment_status` computes unpaid/partially_paid/paid.
- **Limitations:** no idempotency key, no row locks (double-submit can double-pay within the "left" amount race); customer-controlled discount/price directly lowers `must_pay`.

### 4.10 Inventory

- `Ingredient` (restaurant, unit, quantity, min_quantity, price), `ProductIngredient` (recipe), `Supplier`, `StockMovement` (in/out/order). Low-stock notification on threshold crossing. `low-stock` endpoint, per-order ingredient need.
- **Limitations:** `IngredientDetail` PATCH lets chef set `quantity` directly, bypassing movements/audit; no locking; no unit conversion.

### 4.11 Staff, shifts, attendance

- `Staff` (user, restaurant, filial, position, salary, is_active) with plan limit `max_staff`; `StaffShift` start/end; `StaffAttendance` with self check-in/out ("late" if after opening_time).
- **Limitations:** staff can be attached to any user id without consent; salary visible to managers; global role issue (§4.1).

### 4.12 Customers, reviews, favorites, addresses

- `customers/me/` summary, own orders, addresses (single default), favorites, reviews (1–5; if `order` given must be own+completed+same restaurant; one review per order), restaurant rating aggregate.
- **Limitations:** reviews without an order are allowed (fake reviews possible); **any owner/manager can delete any review of any restaurant** [VERIFIED].

### 4.13 Notifications

- `Notification` (per user) and `RestaurantNotification` (per restaurant), created synchronously from model `save()` hooks and views. List/unread-count/read/read-all endpoints.
- **Limitations:** in-app only — no push/SMS/email/WebSocket. Restaurant notifications visible to every staff role ≥ chef of all restaurants they belong to.

### 4.14 Reports & expenses

- Daily (also upserts `DailyReport` — a GET with side effects), daily history, sales (by day / order type), per-filial, top products, payments (by method/status), cancelled orders, expenses CRUD with by-category totals.
- **Limitations:** money is summed per-filial with many queries; cancelled report is N+1; no export (CSV/PDF); `reports/expenses/` list is not paginated.

### 4.15 Subscriptions (SaaS billing)

- `SubscriptionPlan` (price, duration_days, max_filial, max_staff), `RestaurantSubscription`, `SubscriptionPayment`. `subscribe` extends same plan or cancels+creates new; payment is mock/instant. `check_subscriptions` management command (cron) expires and warns 3 days ahead.
- **Limitations:** no real payment; plan write permission uses `IsAdminUser` (`is_staff`) whereas the rest of super-admin uses `is_superuser`; expired subscription does **not** disable anything already created (only blocks new filials/staff).

### 4.16 Coupons & loyalty

- `Coupon` percent/fixed, min order, date window, per-restaurant code (uppercased), one use per customer. Loyalty: 1 point per 10 TJS paid on completion, 1 point = 0.50 TJS, redeem against open order, returned on cancel.
- **Limitations:** completing → cancelling a completed order returns used points but does **not** claw back earned points [CODE]; coupon validity is not rechecked when items are removed (min order).

### 4.17 Delivery

- `DeliveryStaff` (courier per filial), `Delivery` (1:1 order, address, phone, delivery_price, status pending→assigned→picked_up→delivered, timestamps). Manager assigns; courier picks up / delivers → order completed. Notifications to courier and customer.
- **Limitations:** `delivery_price` is client-supplied and may be **negative** [VERIFIED]; `delivery_enabled` setting not enforced; no geolocation/zones/fees.

### 4.18 Audit log, super admin

- `AuditLogMiddleware` logs every successful POST/PUT/PATCH/DELETE under `/api/` (except login/refresh) with user, action, view name, object id. Owners see logs of owned restaurants.
- Super admin: list restaurants, activate/deactivate, platform stats.
- **Limitations:** audit `restaurant` = user's *first* owned/staff restaurant, not the affected one; no before/after diff; `admin/restaurants/<pk>/<action>/` — **any action other than `activate` deactivates** [VERIFIED].

### 4.19 AI (Groq)

- `ai/menu-assistant` (any authenticated user; recommends only real product ids), `ai/product-description` (manager+, optional save), `ai/reviews-summary`, `ai/sales-insights` (manager+), `ai/inventory-forecast` (chef+). Throttle scope `ai` 30/hour/user. JSON mode, 1 retry on 429/invalid JSON, 503 on failure.
- **Limitations:** synchronous 60 s timeout blocks a gunicorn worker (3 workers total); restaurant/product names are interpolated into the system prompt (prompt-injection surface, partially mitigated by instructions).

---

## 5. Frontend audit

**No frontend exists in this repository.** [VERIFIED: no `.html`, `.js`, `.ts`, `.tsx`, `.css`, `package.json`, `templates/`, `static/`, `frontend/` outside `.venv`]

Consequently the following are all **absent**: pages, navigation, components, forms, API client, auth flow (token storage/refresh), role-based UI, responsive layout, animations, dark/light themes, localization (Tajik/Russian/English), accessibility, asset pipeline.

What exists that a frontend can rely on:
- Swagger/ReDoc for developers (not end users).
- Django admin at `/admin/` (default, unbranded) for superusers.
- `RestaurantSettings.language` (default `ru`) and `currency` (default `TJS`) fields — the only localization hooks. Backend messages are English-only strings; Django `USE_I18N=True` but no translations or `gettext` usage.

If a frontend exists elsewhere (another folder/repo), it was not provided and could not be audited. [ASSUMPTION: none exists]

---

## 6. Design & experience audit vs. RESTORA NEXUS direction

| Direction | Current state | Gap |
|---|---|---|
| Cinematic Gastronomy | No UI | Entire visual language to build; menu data supports images per category/product (single image, no gallery/video). |
| Premium 3D architecture | No UI | Needs 3D stack decision (e.g. Three.js / R3F) and performance budget; no 3D assets exist. |
| Dark "Obsidian Cinema" theme | No UI | To build; design tokens needed. |
| Light "Architectural Daylight" theme | No UI | To build. |
| Spatial UI | No UI | To build. |
| Smooth, intentional animations | No UI | To build; must respect `prefers-reduced-motion`. |
| Responsive mobile | No UI | To build; backend images are uploaded at full size (no thumbnails) — mobile bandwidth risk. |
| Tajik / Russian / English | Backend strings English only; spec in Tajik/Russian | Frontend i18n needed; backend error messages need translation keys or `gettext`; product/category names are single-language fields (no translations model). |

Backend features that a premium UX will need but are missing: realtime order/kitchen updates, image thumbnails/responsive sizes, CORS, consistent error envelope, public restaurant listing, multilingual content fields, order-item extras.

---

## 7. Security & performance audit

### 7.1 Exposed secrets — CRITICAL
- `.env.example` line `GROQ_API_KEY=gsk_xVyk…` contains a **real-format Groq key**. `.env.example` is **not** gitignored and is meant to be committed/shared; DEPLOY.md tells operators to `cp .env.example .env`, so the same key propagates to servers. **Action: revoke this key at console.groq.com and replace with a placeholder.** [VERIFIED file content]
- `.env` (gitignored) holds the actual secrets; fine. `db.sqlite3` is gitignored.

### 7.2 Money integrity — CRITICAL [all VERIFIED]
| # | Issue | Location |
|---|---|---|
| S1 | Customer sets `discount` on order create → kept, uncapped (999 on a 60 order) | `serializer.py` OrderSerialiser read_only_fields; `models.py` `Order.calculate_discount` |
| S2 | Customer PATCHes `discount` on own `new` order | `OrderDetail` + same serializer |
| S3 | Customer sets item `price` (0.01 instead of 30) on create and via `PATCH order-products/<pk>/quantity/` | `Bron_productSeria`, `dron_product.save` |
| S4 | Negative `delivery_price` reduces total (65 → 5 TJS) | `DeliverySerializer` / `DeliveryDetail` |
| S5 | Product (and variant) from another restaurant can be added to an order | `AddProduct.perform_create` |
| S6 | Online payments are mocked as instantly paid | `PaymentApi`, `subscribe` (documented as MVP) |

The spec itself (readme §17.4) says: "never accept payment amounts from the frontend only" — S1–S4 violate it.

### 7.3 Authentication handling — HIGH [VERIFIED]
- `PATCH /api/auth/me/ {"password": …}` stores plaintext password.
- `POST /api/auth/change-password/` without `new_password` makes the account unusable; no password validators on register/change.
- No rate limiting on login/register (only AI throttled) → brute-force/credential-stuffing risk. [CODE]
- Refresh rotation off; 1-day refresh lifetime is reasonable.

### 7.4 Missing permission / tenant checks — HIGH [VERIFIED unless noted]
- Waiter assigns a table from another restaurant to an order (`assign_table`).
- Customer attaches another user's reservation to an order.
- Owner/manager moves a filial into another restaurant (`filialApi` update).
- Any owner/manager deletes reviews of any restaurant (`ReviewDetail.perform_destroy`).
- Global role overwrite: owner demoted to `customer` by `staff_role`.
- Super-admin action typo deactivates restaurant.
- [CODE] `change_role` lets an owner grant `owner` to any of their staff; `RestaurantSettingsDetail`, `IngredientDetail`, `SupplierDetail`, `CouponDetail`, `ExpenseDetail`, `KitchenDetail`, `StaffShiftDetail`, `DeliveryStaffDetail` updates don't re-check that a changed FK (restaurant/filial/staff) still belongs to the user — same class of bug as the filial move.
- [CODE] `assign_customer` lets staff attach any user id to an order (enumeration of user ids).
- [CODE] `StolApi`: waiter may DELETE tables. `DronStolDetail`: any filial staff (e.g. chef) may edit/delete reservations.

### 7.5 Business-logic integrity — MEDIUM
- Unrestricted order status transitions (completed → new) [VERIFIED]; reservations in the past [VERIFIED].
- No `select_for_update` on loyalty balance, ingredient stock, payments → race conditions. [CODE]
- GET `reports/daily/` writes to DB. [CODE]

### 7.6 Performance — N+1 and query volume [VERIFIED measurements]
- `GET /api/order-products/` with 14 items → **119 SQL queries** (nested Order→Filial→Restaurant, Product→Category→Restaurant, Variant→Product… serializers without `select_related`).
- Creating one order item → 5 queries (item save + order double-save + delivery lookup); each item save re-sums all items.
- [CODE] Same pattern in `OrderSerialiser` (nests Filial, Stol→Filial→Restaurant, Reservation→…), `MenuSerializer` (2 queries per product), `KitchenOrderSerializer` (items + preparation time each query), `filial_stats` (≈8 queries per filial), `cancelled_report` (1 per order), `restaurant_rating` (6 queries + Python sum), `customer_me` total_spent in Python.
- AI calls are synchronous (≤60 s ×2) on 3 gunicorn workers → a few concurrent AI requests can starve the API.
- Images served at original size; no thumbnails/WebP.

### 7.7 Infrastructure
- Good: non-root container, DEBUG off by default, HSTS, TLS redirect, secrets from env, DB healthcheck, backups via cron.
- Missing: CORS, security headers for media (Content-Disposition for uploads), nginx caching headers for static/media, gzip/brotli, Sentry/error tracking, structured logs, health endpoint, `CONN_MAX_AGE`.
- `migrate` runs on every container start in all 3 gunicorn replicas' parent — fine for one container, racy if scaled.

### 7.8 Accessibility / mobile
- Not applicable yet (no UI). Backend-side mobile risks: full-size images, heavy nested JSON payloads (e.g. every order item embeds full order, product, category and restaurant objects).

---

## 8. Missing features (relative to spec and RESTORA NEXUS)

1. Entire frontend (customer app, restaurant dashboard, kitchen display, super-admin panel) — spec §11.
2. Realtime updates (Channels/WebSocket or SSE) — spec Phase 3.7.
3. Real online payment gateway — spec Phase 3.8.
4. CORS configuration for a browser frontend.
5. Order-item extras (model exists, no linkage).
6. Remove order item endpoint.
7. Enforcement of `RestaurantSettings` (hours, delivery/reservation toggles).
8. Multilingual content (tg/ru/en) for menu/restaurant fields and API messages.
9. Image thumbnails / responsive images.
10. Public (anonymous) restaurant & filial discovery.
11. Order status state machine.
12. Per-restaurant roles (membership model) instead of a global role.
13. django-filter / consistent filtering & ordering, rate limiting on auth.
14. Background jobs (Celery) for AI, notifications, reports.
15. Push/SMS/email notifications.

---

## 9. Verification log

| Check | Result |
|---|---|
| `manage.py check` | 0 issues |
| `manage.py makemigrations --check --dry-run` | No changes detected |
| `manage.py test myapp` | 33 tests, OK |
| `manage.py spectacular --validate` (output to scratchpad) | exit 0, 0 warnings |
| Exploit probe (throwaway test DB, scratchpad script) | 16 issues CONFIRMED, see §7; numbers in §7.6 measured |
| Not tested | PostgreSQL behaviour, Docker/nginx build & TLS, real Groq calls, concurrency/race conditions, load |

No project source, model, migration, URL or setting was modified during this audit. Only the four `RESTORA_*.md` files were added to the project root.
