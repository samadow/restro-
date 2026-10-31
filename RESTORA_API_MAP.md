# RESTORA — API Map (Phase 0)

Built **only** from `server/urls.py`, `myapp/urls.py`, `myapp/views.py`, `myapp/serializer.py`, `myapp/permissions.py`, `server/settings.py`. Date: 2026-10-31.

## Conventions

- Base URL: `/api/` (from `server/urls.py`). All paths below are absolute.
- **Auth** column: `JWT` = `Authorization: Bearer <access>` required; `Public` = no auth (DRF default `AllowAny`); `Public read` = GET anonymous, writes need JWT (`IsAuthenticatedOrReadOnly`).
- **Perm** column: role permission class (superuser passes all):
  `IsOwner`=owner · `IsManager`=owner,manager · `IsChef`=owner,manager,chef · `IsWaiter`=owner,manager,waiter,cashier · `IsDelivery`=owner,manager,delivery · `IsSuperAdmin`=is_superuser · `IsAdminUser`=is_staff.
  "scoped" = queryset limited by `my_restaurants` / `my_filials` / `my_orders` (tenant isolation).
- **Tested**: `T` = covered by `myapp/tests.py` (passing) · `P` = exercised by audit probe on throwaway DB · `—` = verified by reading code only.
- List responses are paginated `{count, next, previous, results:[…]}` (`?page`, `?page_size` ≤ 100) unless stated.
- Errors raised as exceptions: `{"error", "details", "status_code"}`. Errors returned directly by FBVs: `{"error": …}` (sometimes with extra keys) or raw serializer errors.
- Writable fields = serializer `fields` minus `read_only_fields`; `(opt)` = not required. Image fields require `multipart/form-data`.
- Aliases: identical view mounted on more than one URL — listed on one row.

---

## 0. Platform / docs (server/urls.py)

| Method | URL | View | Auth | Notes |
|---|---|---|---|---|
| GET | `/admin/` | Django admin | session, superuser/staff | all models registered with default admin |
| GET | `/api/schema/` | SpectacularAPIView | Public | OpenAPI 3; validates with 0 warnings [VERIFIED] |
| GET | `/api/docs/`, `/swagger/` | SpectacularSwaggerView | Public | duplicate Swagger UI |
| GET | `/api/redoc/` | SpectacularRedocView | Public | |
| GET | `/media/…` | static() | Public | only when `DEBUG=True`; nginx in prod |

---

## 1. Accounts & auth

| Method | URL | View | Serializer | Auth / Perm | Request | Response | Tested | Limitations / bugs |
|---|---|---|---|---|---|---|---|---|
| POST | `/api/auth/register/`, `/api/register/` | RegisterApi (CreateAPIView) | CustumerSerializers | Public | `username, phon_number, password` | 201 `{username, phon_number}` | T | no password validators; creates empty Profile |
| POST | `/api/auth/login/`, `/api/login/` | TokenObtainPairView | SimpleJWT | Public | `username, password` | `{access, refresh}` | T | no rate limit |
| POST | `/api/auth/refresh/`, `/api/token/refresh/` | TokenRefreshView | SimpleJWT | Public | `refresh` | `{access}` | T | no rotation |
| POST | `/api/auth/logout/`, `/api/logout/` | LogoutView | — | JWT | `refresh` | 205 `{detail}` / 400 | T | |
| GET | `/api/auth/me/` | MyProfile | CustumerSerializers | JWT | — | `{username, phon_number}` | T | returns no id/role/fullname |
| PATCH | `/api/auth/me/` | MyProfile | CustumerSerializers | JWT | `username, phon_number, password` (opt) | same | P | **BUG: `password` saved in plaintext** |
| POST | `/api/auth/change-password/` | change_password | — | JWT | `old_password, new_password` | `{message}` | P | **BUG: missing `new_password` → unusable account**; no validators |
| PATCH | `/api/auth/users/<pk>/role/` | change_role | — | JWT · IsOwner · user must be staff of owner's restaurant | `role` ∈ ROLE_CHOICES | `{message, user, role}` | — | can grant `owner`; role is global |
| POST | `/api/profil_cr/` | Profil_cr | ProfillSerializer | JWT | `fullname, bio, phon_number, img(opt)` | 201 profile | — | **always 400 for registered users** (profile auto-created); error text points to `/auth/me/` which edits a different model |
| GET/PUT/PATCH/DELETE | `/api/profile/<pk>/` | ProfilApi | ProfillSerializer `{id, fullname, bio, phon_number, img, role(ro)}` | JWT · own profile (superuser: all) | same fields | profile | — | pk is Profile id, not user id; client must discover it via `/customers/me/` |
| GET | `/api/customers/me/` | customer_me | — | JWT | — | `{id, username, phon_number, role, profile{…}, default_address, orders_count, total_spent, favorites_count, reviews_count}` | — | `total_spent` summed in Python |

## 2. Restaurants, settings, filials, staff

| Method | URL | View | Serializer | Auth / Perm | Request | Tested | Limitations / bugs |
|---|---|---|---|---|---|---|---|
| GET | `/api/restaurants/` | RestaurantList | RestarantSSerializers `{id, name, description, address, phone_number, img, owner(ro)}` | JWT | `?search` | P (401 anon) | active + mine; **not public**; `is_active` not in payload |
| POST | `/api/restaurants/`, `/api/resta_cr/` | RestaurantList / Cr_rest | same | JWT (any user) | `name, description, address, phone_number, img` (multipart) | T | caller becomes `owner` |
| GET | `/api/restaurants/<pk>/`, `/api/Restarant/<pk>/` | RestarantApi | same | JWT | — | — | active or mine |
| PUT/PATCH/DELETE | same | RestarantApi | same | JWT · owner of restaurant (scoped) | fields above | T (PATCH) | other owner → 404 |
| GET | `/api/restaurants/<pk>/rating/` | restaurant_rating | — | Public | — | — | `{restaurant_id, restaurant, rating, reviews_count, stars{5..1}}` |
| GET/POST | `/api/restaurant-settings/` | RestaurantSettingsApi | RestaurantSettingsSerializer `{id, restaurant, currency, language, opening_time, closing_time, delivery_enabled, reservation_enabled}` | JWT · IsManager · scoped | all fields | — | settings mostly **not enforced** |
| GET/PUT/PATCH | `/api/restaurant-settings/<pk>/` | RestaurantSettingsDetail | same | JWT · IsManager · scoped | — | — | `restaurant` FK change not re-checked |
| GET | `/api/filials/` | FilialList | FilialSerializer `{id, name, phone_number, address, restaurant, restaurant_id(nested ro), img, is_active}` | JWT | `?restaurant, ?is_active` | — | customers: active filials of active restaurants; staff: own |
| POST | `/api/filials/`, `/api/cr_filial/` | FilialList / cr_filial | same | JWT · owner of restaurant · active subscription · plan `max_filial` | `name, phone_number, address, restaurant, img, is_active(opt)` | T | |
| GET | `/api/filials/<pk>/`, `/api/filial/<pk>/` | filialApi | same | JWT | — | — | returns any filial incl. inactive |
| PUT/PATCH | same | filialApi | same | JWT · owner/manager · scoped | fields | P | **BUG: `restaurant` can be changed to a foreign restaurant** |
| DELETE | same | filialApi | — | JWT · owner of restaurant | — | — | |
| GET/POST | `/api/staff/` | StaffApi | StaffSerializer `{id, user, username(ro), restaurant, filial, filial_name(ro), position, salary, is_active, cr_at(ro)}` | JWT · IsManager · scoped | `?restaurant, ?filial, ?position, ?is_active`; POST all fields | T (403 customer), P | plan `max_staff`; recomputes user role (**overwrites owner role**) |
| GET/PUT/PATCH/DELETE | `/api/staff/<pk>/` | StaffDetail | same | JWT · IsManager · scoped | — | P | delete → role reset to `customer` even for owners |

## 3. Tables & reservations

| Method | URL | View | Serializer | Auth / Perm | Request | Tested | Limitations / bugs |
|---|---|---|---|---|---|---|---|
| GET | `/api/tables/` | StolList | StolSerializers `{id, name, description, capacity, status, filial, filial_id(nested ro)}` | JWT | `?filial, ?status` | — | customers see all tables of active filials |
| POST | `/api/tables/`, `/api/cr_stol/` | StolList / cr_Stol | same | JWT · owner/manager · scoped filial | `name, description, capacity, status, filial` | — | |
| GET | `/api/tables/<pk>/`, `/api/stol/<pk>/` | StolApi | same | JWT | — | — | any table |
| PUT/PATCH/DELETE | same | StolApi | same | JWT · owner/manager/**waiter** · scoped | — | — | waiter can delete tables |
| GET | `/api/tables/<pk>/available/` | stol_available | — | JWT | `?date=YYYY-MM-DD&vakt=HH:MM[&end_time=HH:MM]` | — | `{stol_id, date, vakt, available}`; default slot 2 h |
| GET | `/api/reservations/` | DronStolList | DronStolSerializer `{id, user(ro), filial, filial_id, stol, stol_id, date, vakt, end_time, guests, status(ro), comment}` | JWT · own or my filials | `?filial, ?date, ?status` | — | |
| POST | `/api/reservations/` | DronStolList | same | JWT | `filial, stol, date, vakt, end_time(opt), guests, comment` | T, P | overlap/capacity checked; **past dates accepted**; hours / `reservation_enabled` ignored |
| GET/PUT/PATCH/DELETE | `/api/reservations/<pk>/` | DronStolDetail | same | JWT · own or my filials | — | — | any filial staff (even chef) can edit/delete; customer can hard-delete |
| POST | `/api/reservations/<pk>/cancel/` | cancel_reservation | — | JWT · own or my filials | — | T | `{message, reservation_id, status}` |
| PATCH | `/api/reservations/<pk>/status/` | change_reservation_status | — | JWT · IsWaiter · scoped | `status` ∈ pending/confirmed/cancelled/completed/no_show | — | no transition rules |

## 4. Menu

| Method | URL | View | Serializer | Auth / Perm | Request | Tested | Limitations |
|---|---|---|---|---|---|---|---|
| GET | `/api/menu/` | MenuApi | MenuSerializer `{id, name, description, img, restaurant, products[{id, name, decription, price, preparation_time, img, variants[{id,name,price}], extras[{id,name,price}]}]}` | Public | `?restaurant` | T, P | N+1 (2 queries/product) |
| GET | `/api/categories/`, `/api/categoryapi/` | CategoruApi | CategorySerialiyser `{id, name, description, restaurant, img, restaurant_id(nested ro), is_active}` | Public read | — | — | no filters (all restaurants, incl. inactive) |
| POST | same | CategoruApi | same | JWT · owner/manager of restaurant | `name, description, restaurant, img, is_active` | — | |
| GET/PUT/PATCH/DELETE | `/api/categories/<pk>/`, `/api/categoryapi/<pk>/` | CategoryDetail | same | Public read / owner-manager write | — | — | |
| GET | `/api/products/`, `/api/productApi/` | ProductApi | ProductSerialayzer `{id, name, decription, price, preparation_time, img, category, categori_id(nested ro), is_available}` | Public read | `?search, ?category, ?restaurant, ?is_available=true/false, ?min_price, ?max_price` | P | returns unavailable / inactive-restaurant products by default |
| POST | same | ProductApi | same | JWT · owner/manager of restaurant | fields (multipart) | T | |
| GET/PUT/PATCH/DELETE | `/api/products/<pk>/`, `/api/productApi/<pk>/` | ProductDetail | same | Public read / owner-manager write | — | — | |
| GET/POST | `/api/product-variants/` | ProductVariantApi | ProductVariantSeriali `{id, name, price, product, product_id(nested ro), is_active}` | Public read / owner-manager write | — | — | no `?product` filter |
| GET/PUT/PATCH/DELETE | `/api/product-variants/<pk>/` | ProductVariantDetail | same | same | — | — | |
| GET/POST | `/api/product-extras/` | ProductExtraApi | ProductExtraSeriali `{id, name, price, is_active, product, product_id}` | same | — | — | extras can't be ordered |
| GET/PUT/PATCH/DELETE | `/api/product-extras/<pk>/` | ProductExtraDetail | same | same | — | — | |

## 5. Orders & order items

| Method | URL | View | Serializer | Auth / Perm | Request | Tested | Limitations / bugs |
|---|---|---|---|---|---|---|---|
| GET | `/api/orders/` | OrderApi | OrderSerialiser `{id, user(ro), filial, filial_id, stol, stol_id, reservation, reservation_id, order_number, order_type, status(ro), total_price(ro), comment, discount, coupon(ro), points_used(ro)}` | JWT · my_orders | `?filial, ?status` | T, P | heavy nested payload |
| POST | `/api/orders/` | OrderApi | same | JWT; staff must belong to filial | `filial, stol(opt), reservation(opt), order_type(opt), comment(opt), order_number(opt), discount(opt)` | T, P | **BUG: `discount` writable**; **BUG: foreign `reservation` accepted**; table set busy |
| GET | `/api/orders/<pk>/` | OrderDetail | same | JWT · my_orders | — | T | |
| PUT/PATCH/DELETE | `/api/orders/<pk>/` | OrderDetail | same | JWT · staff (owner/manager/waiter/cashier) scoped; customer only own `new` | — | P | **BUG: customer PATCH `discount`**; can change filial; hard delete allowed |
| GET | `/api/order-products/` | AddProduct | Bron_productSeria `{id, kalichestvo, total_price(ro), price, order, order_id(nested), variant, variant_id(nested), product, product_id(nested), comment}` | JWT · items of my_orders | — | P | **119 queries for 14 items** |
| POST | `/api/order-products/` | AddProduct | same | JWT · order in my_orders, not completed/cancelled | `order, product, variant(opt), kalichestvo, comment(opt), price(opt)` | T, P | **BUG: client `price` accepted**; **BUG: foreign product/variant accepted** |
| PATCH | `/api/order-products/<pk>/quantity/` | update_quantity | Bron_productSeria (partial) | JWT · my_orders | any writable field | — | same `price` bug; no status check (can edit completed orders) |
| GET | `/api/order-products/<pk>/total/` | calculate_total | — | JWT · my_orders | — | — | `{product, price, quantity, total_price}` |
| PATCH | `/api/orders/<pk>/assign-table/` | assign_table | — | JWT · IsWaiter · my_orders | `stol` | P | **BUG: table of any restaurant accepted**; old table not freed; new not set busy |
| PATCH | `/api/orders/<pk>/assign-customer/` | assign_customer | — | JWT · IsWaiter · my_orders | `user` | — | any user id |
| PATCH | `/api/orders/<pk>/status/` | change_order_status | — | JWT · IsWaiter · my_orders | `status` ∈ ORDER_STATUS | T, P | **no state machine** (completed→new allowed) |
| POST/PATCH | `/api/orders/<pk>/cancel/` | cancel_order | — | JWT · my_orders; customer only from `new` | — | — | ingredients not returned to stock |
| POST | `/api/orders/<pk>/send-to-kitchen/` | send_to_kitchen | — | JWT · IsWaiter · my_orders; status new/confirmed | — | T | `{message, order_id, kitchen_order_id, status}`; checks & deducts ingredients |
| GET | `/api/orders/<pk>/history/` | get_order_history | — | JWT · my_orders | — | — | `{order_id, history[{old_status,new_status,changed_by,date}]}` |
| POST/PATCH | `/api/orders/<pk>/complete/` | complete_order | — | JWT · IsWaiter · status ready/served | — | — | |
| GET | `/api/orders/<pk>/ingredients/` | get_order_ingredients | — | JWT · IsChef · my_orders | — | — | |
| GET | `/api/orders/<pk>/payment-status/` | order_payment_status | — | JWT · my_orders | — | — | `{order_id, total_price, discount, must_pay, paid, left, payment_status}` |
| POST | `/api/orders/<pk>/apply-coupon/` | apply_coupon | — | JWT · my_orders | `code` | T | `{message, order_id, code, total_price, discount, must_pay}` |
| DELETE | `/api/orders/<pk>/apply-coupon/` | apply_coupon | — | same | — | — | removes coupon |
| GET | `/api/customers/me/orders/` | CustomerOrdersApi | OrderSerialiser | JWT · own | `?status` | — | |

## 6. Kitchen

| Method | URL | View | Serializer | Auth / Perm | Request | Tested | Notes |
|---|---|---|---|---|---|---|---|
| GET/POST | `/api/kitchens/` | KitchenApi | KitchenSerializer `{id, filial, name, is_active}` | JWT · IsManager · scoped | — | — | |
| GET/PUT/PATCH/DELETE | `/api/kitchens/<pk>/` | KitchenDetail | same | JWT · IsManager · scoped | — | — | filial FK change not re-checked |
| GET | `/api/kitchen/orders/` | KitchenOrderList | KitchenOrderSerializer `{id, order, order_number, stol, kitchen, status, order_time, cr_at, started_at, finished_at, preparation_time, cooking_minutes, items[{id, product, variant, kalichestvo, comment, preparation_time, status, started_at, finished_at}]}` | JWT · IsChef · scoped | `?kitchen, ?filial, ?status` (default excludes ready) | T | oldest first; poll-only |
| GET | `/api/kitchen/orders/<pk>/` | KitchenOrderDetail | same | JWT · IsChef · scoped | — | — | |
| POST | `/api/kitchen/orders/<pk>/start/` | kitchen_start | same | JWT · IsChef | — | T | pending → preparing |
| POST | `/api/kitchen/orders/<pk>/ready/` | kitchen_ready | same | JWT · IsChef | — | T | → ready, order → ready |
| POST | `/api/kitchen/items/<pk>/ready/` | kitchen_item_ready | same | JWT · IsChef | — | — | last item auto-readies ticket |

## 7. Payments

| Method | URL | View | Serializer | Auth / Perm | Request | Tested | Notes |
|---|---|---|---|---|---|---|---|
| GET | `/api/payments/` | PaymentApi | PaymentSerializer `{id, order, order_number, user(ro), amount, payment_method, status(ro), transaction_id(ro), refunds[…], cr_at}` | JWT · my_orders | `?order, ?status, ?method` | — | |
| POST | `/api/payments/` | PaymentApi | same | JWT; owner/manager/cashier any method; customer own order **online only** | `order, payment_method, amount(opt = remaining)` | T | **online is MOCK** (instant paid) |
| GET | `/api/payments/<pk>/` | PaymentDetail | same | JWT · my_orders (customers own) | — | — | |
| POST | `/api/payments/<pk>/refund/` | refund_payment | RefundSerializer `{amount(opt), reason}` | JWT · IsManager · scoped | `amount, reason` | T | `{message, refund_id, payment_id, amount, payment_status}` |

## 8. Inventory

| Method | URL | View | Serializer | Auth / Perm | Request | Tested | Notes |
|---|---|---|---|---|---|---|---|
| GET/POST | `/api/inventory/ingredients/` | IngredientApi | IngredientSerializer `{id, restaurant, name, unit, quantity, min_quantity, price, is_low(ro), cr_at}` | JWT · IsChef · scoped | `?restaurant, ?search, ?low=true` | T | |
| GET/PUT/PATCH/DELETE | `/api/inventory/ingredients/<pk>/` | IngredientDetail | same | JWT · IsChef · scoped | — | — | `quantity` editable directly (bypasses movements) |
| GET | `/api/inventory/low-stock/` | low_stock | — | JWT · IsChef | `?restaurant` | — | `{count, ingredients[…]}` (not paginated) |
| GET/POST | `/api/inventory/suppliers/` | SupplierApi | SupplierSerializer `{id, restaurant, name, phone_number, address, cr_at}` | JWT · IsManager · scoped | `?restaurant` | — | |
| GET/PUT/PATCH/DELETE | `/api/inventory/suppliers/<pk>/` | SupplierDetail | same | JWT · IsManager · scoped | — | — | |
| GET/POST | `/api/inventory/product-ingredients/` | ProductIngredientApi | ProductIngredientSerializer `{id, product, product_name, ingredient, ingredient_name, unit, quantity}` | JWT · IsChef · scoped | `?product` | — | same-restaurant check on create only |
| GET/PUT/PATCH/DELETE | `/api/inventory/product-ingredients/<pk>/` | ProductIngredientDetail | same | JWT · IsChef · scoped | — | — | |
| GET/POST | `/api/inventory/stock-movements/` | StockMovementApi | StockMovementSerializer `{id, ingredient, ingredient_name, supplier, supplier_name, movement_type, quantity, price(opt), comment, cr_at}` | JWT · IsChef · scoped | `?ingredient, ?supplier, ?type` | T | `order` type rejected (auto only) |

## 9. Staff shifts & attendance

| Method | URL | View | Serializer | Auth / Perm | Request | Notes |
|---|---|---|---|---|---|---|
| GET/POST | `/api/staff/shifts/` | StaffShiftApi | StaffShiftSerializer `{id, staff, username, start_time(opt), end_time(ro), status(ro), hours, cr_at}` | JWT · IsManager · scoped | `?staff, ?filial, ?status, ?date` | one active shift per staff |
| GET/PUT/PATCH/DELETE | `/api/staff/shifts/<pk>/` | StaffShiftDetail | same | JWT · IsManager · scoped | — | |
| POST | `/api/staff/shifts/<pk>/end/` | end_shift | same | JWT · IsManager | — | |
| GET/POST | `/api/staff/attendance/` | StaffAttendanceApi | StaffAttendanceSerializer `{id, staff, username, date(opt), check_in, check_out, status}` | JWT · IsManager · scoped | `?staff, ?filial, ?date, ?status` | one per day |
| GET/PUT/PATCH/DELETE | `/api/staff/attendance/<pk>/` | StaffAttendanceDetail | same | JWT · IsManager · scoped | — | |
| POST | `/api/staff/attendance/check-in/` | check_in | same | JWT · must be active Staff | — | `late` if after opening_time |
| POST | `/api/staff/attendance/check-out/` | check_out | same | JWT · active Staff | — | |

(None of §9 is covered by tests.)

## 10. Customers, reviews

| Method | URL | View | Serializer | Auth / Perm | Request | Tested | Notes |
|---|---|---|---|---|---|---|---|
| GET/POST | `/api/customers/me/addresses/` | CustomerAddressApi | CustomerAddressSerializer `{id, address, city, is_default}` | JWT · own | — | — | first address auto-default |
| GET/PUT/PATCH/DELETE | `/api/customers/me/addresses/<pk>/` | CustomerAddressDetail | same | JWT · own | — | — | |
| GET/POST | `/api/customers/me/favorites/` | CustomerFavoriteApi | CustomerFavoriteSerializer `{id, restaurant, restaurant_id(nested), cr_at}` | JWT · own | `restaurant` | — | |
| GET/DELETE | `/api/customers/me/favorites/<pk>/` | CustomerFavoriteDetail | same | JWT · own | — | — | |
| GET | `/api/reviews/` | ReviewApi | ReviewSerializer `{id, user(ro), username, restaurant, order, rating 1–5, comment, cr_at}` | Public | `?restaurant, ?user, ?rating` | P | |
| POST | `/api/reviews/` | ReviewApi | same | JWT | `restaurant, rating, comment, order(opt)` | — | review without order allowed |
| GET | `/api/reviews/<pk>/` | ReviewDetail | same | Public | — | — | |
| PUT/PATCH | `/api/reviews/<pk>/` | ReviewDetail | same | JWT · author only | `rating, comment` | — | |
| DELETE | `/api/reviews/<pk>/` | ReviewDetail | — | JWT · author or **any** owner/manager | — | P | **BUG: cross-restaurant delete** |

## 11. Notifications

| Method | URL | View | Auth / Perm | Notes |
|---|---|---|---|---|
| GET | `/api/notifications/` | NotificationApi (NotificationSerializer `{id, title, message, notification_type, is_read, cr_at}`) | JWT · own | `?is_read, ?type` |
| GET | `/api/notifications/unread-count/` | unread_count | JWT | `{unread}` |
| POST | `/api/notifications/<pk>/read/` | read_notification | JWT · own | |
| POST | `/api/notifications/read-all/` | read_all_notifications | JWT | `{message, count}` |
| GET | `/api/restaurant-notifications/` | RestaurantNotificationApi | JWT · IsChef · my_restaurants | `?restaurant, ?is_read, ?type` |
| POST | `/api/restaurant-notifications/<pk>/read/` | read_restaurant_notification | JWT · IsChef | |
| POST | `/api/restaurant-notifications/read-all/` | read_all_restaurant_notifications | JWT · IsChef | `restaurant` (opt, body or query) |

(Not covered by tests.)

## 12. Reports & expenses (all `JWT · IsManager`, scoped to `my_filials`, filters `?restaurant, ?filial`)

| Method | URL | View | Extra params | Response |
|---|---|---|---|---|
| GET | `/api/reports/daily/` | daily_report | `?date` | `{date, total{…}, filials[{filial_id, filial, restaurant_id, total_orders, completed_orders, cancelled_orders, sales, payments, refunds, expenses, profit}]}` — **also writes DailyReport rows** |
| GET | `/api/reports/daily/history/` | DailyReportHistory (DailyReportSerializer) | `?date_from, ?date_to` (default last 30 days) | paginated |
| GET | `/api/reports/sales/` | sales_report | date range | `{date_from, date_to, total_orders, completed_orders, cancelled_orders, sales, discounts, average_check, by_day[], by_order_type[]}` (T: 403 for chef) |
| GET | `/api/reports/filials/` | filials_report | date range | `{…, total, filials[]}` |
| GET | `/api/reports/products/` | products_report | date range, `?category, ?order_by=revenue, ?limit` | `{…, products[{product_id, product, category, quantity, revenue, orders}]}` |
| GET | `/api/reports/payments/` | payments_report | date range | `{payments_count, paid, refunded, refunds_count, net, by_method[], by_status[]}` |
| GET | `/api/reports/cancelled/` | cancelled_report | date range | `{count, lost_amount, by_filial[], orders[]}` (N+1) |
| GET | `/api/reports/expenses/` | ExpenseApi (ExpenseSerializer `{id, restaurant, filial, filial_name, title, amount, category, comment, date(opt), cr_at}`) | `?category`, date range | **not paginated**: `{count, total, by_category[], expenses[]}` |
| POST | `/api/reports/expenses/` | ExpenseApi | — | filial must be mine & in restaurant |
| GET/PUT/PATCH/DELETE | `/api/reports/expenses/<pk>/` | ExpenseDetail | — | FK change not re-checked |

(Only `reports/sales/` permission covered by tests.)

## 13. Subscriptions (SaaS)

| Method | URL | View | Auth / Perm | Request / Response | Tested |
|---|---|---|---|---|---|
| GET | `/api/subscriptions/plans/` | SubscriptionPlanApi (SubscriptionPlanSerializer `{id, name, description, price, duration_days, max_filial, max_staff, is_active}`) | Public | active plans (is_staff: all) | P |
| POST | same | same | JWT · **IsAdminUser (is_staff)** | plan fields | — |
| GET | `/api/subscriptions/plans/<pk>/` | SubscriptionPlanDetail | Public | — | — |
| PUT/PATCH/DELETE | same | same | JWT · IsAdminUser | — | — |
| GET | `/api/subscriptions/current/` | current_subscription | JWT · IsManager · `?restaurant` required | `{restaurant_id, active, subscription{…days_left}, usage{filials, max_filial, staff, max_staff}}` | — |
| POST | `/api/subscriptions/subscribe/` | subscribe (SubscribeSerializer) | JWT · IsOwner · own restaurant | `restaurant, plan, payment_method` → 201 `{message, subscription, payment}`; **mock payment** | T |
| GET | `/api/subscriptions/payments/` | SubscriptionPaymentApi | JWT · IsManager · scoped | `?restaurant, ?status` | — |
| GET | `/api/subscriptions/history/` | SubscriptionHistory | JWT · IsManager · scoped | `?restaurant` | — |

## 14. Coupons & loyalty

| Method | URL | View | Auth / Perm | Request / Response | Tested |
|---|---|---|---|---|---|
| GET/POST | `/api/coupons/` | CouponApi (CouponSerializer `{id, restaurant, code, discount_type, discount_value, min_order_price, start_date, end_date, is_active, cr_at}`) | JWT · IsManager · scoped | `?restaurant, ?is_active`; code uppercased & unique per restaurant | — |
| GET/PUT/PATCH/DELETE | `/api/coupons/<pk>/` | CouponDetail | JWT · IsManager · scoped | uniqueness not rechecked on update | — |
| POST | `/api/coupons/validate/` | validate_coupon | JWT | `code` + (`order` \| `restaurant`+`amount`) → `{valid, code, discount_type, discount_value, amount, discount, amount_after_discount}` | — |
| GET | `/api/loyalty/` | LoyaltyApi (LoyaltyAccountSerializer `{id, restaurant, restaurant_name, points, points_price, transactions[≤20], cr_at}`) | JWT · own | `?restaurant` | — |
| POST | `/api/loyalty/redeem/` | redeem_points | JWT · own order | `order, points` → `{message, order_id, points_used, points_left, discount, must_pay}` | — |

## 15. Delivery

| Method | URL | View | Auth / Perm | Request / Response | Tested |
|---|---|---|---|---|---|
| GET/POST | `/api/delivery/staff/` | DeliveryStaffApi (DeliveryStaffSerializer `{id, user, username, filial, filial_name, vehicle, is_active}`) | JWT · IsManager · scoped | `?filial, ?is_active`; user role → delivery | T |
| GET/PUT/PATCH/DELETE | `/api/delivery/staff/<pk>/` | DeliveryStaffDetail | JWT · IsManager · scoped | — | — |
| GET | `/api/delivery/orders/` | DeliveryApi (DeliverySerializer `{id, order, order_number, order_status, must_pay, delivery_staff(ro), courier, address, phone_number, delivery_price, status(ro), picked_up_at, delivered_at, cr_at, updated_at}`) | JWT · my_orders or my deliveries (courier: assigned only) | `?status, ?filial` | T |
| POST | `/api/delivery/orders/` | DeliveryApi | JWT · order in my_orders | `order, address, phone_number, delivery_price` | T, P — **BUG: negative/arbitrary `delivery_price`** |
| GET/PUT/PATCH | `/api/delivery/orders/<pk>/` | DeliveryDetail | JWT · scoped; only while `pending` | same fields | — same price bug |
| POST | `/api/delivery/orders/<pk>/assign/` | assign_delivery | JWT · IsManager | `delivery_staff` (same filial, active) | T |
| POST | `/api/delivery/orders/<pk>/picked-up/` | picked_up_delivery | JWT · IsDelivery · assigned courier | — | T |
| POST | `/api/delivery/orders/<pk>/delivered/` | delivered_delivery | JWT · IsDelivery · assigned courier | → order completed | T |

## 16. Audit log & super admin

| Method | URL | View | Auth / Perm | Notes | Tested |
|---|---|---|---|---|---|
| GET | `/api/audit-logs/` | AuditLogApi (AuditLogSerializer `{id, user, username, restaurant, action, model_name, object_id, description, cr_at}`) | JWT · IsOwner (owned restaurants; superuser all) | `?user, ?action, ?model, ?date` | T |
| GET | `/api/admin/restaurants/` | AdminRestaurantApi (AdminRestaurantSerializer `{id, name, owner, owner_username, phone_number, address, is_active, filials, subscription, cr_at}`) | JWT · IsSuperAdmin | `?search, ?is_active` | T |
| POST | `/api/admin/restaurants/<pk>/<action>/` | admin_restaurant_active | JWT · IsSuperAdmin | `action` = `activate` / `deactivate` — **BUG: any other string deactivates** | T, P |
| GET | `/api/admin/stats/` | admin_stats | JWT · IsSuperAdmin | `{users, restaurants, active_restaurants, filials, orders, orders_today, sales, active_subscriptions, subscription_income}` | T |

## 17. AI (Groq) — throttle scope `ai` (default 30/hour/user); 503 `{error}` when AI unavailable/not configured

| Method | URL | View | Auth / Perm | Request | Response | Tested (Groq mocked) |
|---|---|---|---|---|---|---|
| POST | `/api/ai/menu-assistant/` | ai_menu_assistant | JWT (any) | `restaurant, message (≤1000), history[{role, content}] (≤10)` | `{answer, products[{id,name,price}], total_price}` | T |
| POST | `/api/ai/product-description/` | ai_product_description | JWT · IsManager · own restaurant | `product, language(opt, ru), save(opt)` | `{product_id, description, short, saved}` | T |
| GET | `/api/ai/reviews-summary/` | ai_reviews_summary | JWT · IsManager | `?restaurant, ?language` | `{restaurant_id, reviews_count, rating, summary, positives, negatives, advice}` | T |
| GET | `/api/ai/sales-insights/` | ai_sales_insights | JWT · IsManager | `?restaurant, ?date_from, ?date_to, ?language` | `{…, summary, insights, recommendations, warnings, data}` | — |
| GET | `/api/ai/inventory-forecast/` | ai_inventory_forecast | JWT · IsChef | `?restaurant, ?days (1–90), ?language` | `{restaurant_id, days, summary, buy_list[], warnings[], ingredients[]}` | T |

---

## 18. Classification

### 18.1 Confirmed working (tested, behaviour correct for the tested path)
Auth register/login/refresh/logout/me(GET); restaurant create & owner PATCH isolation; filial create with subscription limit; subscribe; product create permissions; public menu; reservation create/overlap/cancel; order create + item add total (with server prices); send-to-kitchen → kitchen start/ready → order ready; coupon apply + loyalty earn; cashier payment + manager partial refund; customer online (mock) payment; stock movements + ingredient deduction; ingredient isolation; customer/other-owner order isolation; full delivery flow; super-admin list/deactivate/stats; audit log; AI endpoints (with mocked Groq) except sales-insights; role 403s for customer on kitchen/reports/inventory/staff.

### 18.2 Existing but incomplete
- Online payments & subscription payments — **mock**, no gateway.
- `restaurant-settings` — stored but not enforced (hours, delivery/reservation toggles).
- `product-extras` — CRUD only; cannot be ordered.
- Order items — no remove endpoint; edits only via `/quantity/`.
- `kitchens` — only the first active kitchen of a filial is used.
- Notifications — in-app polling only.
- `reports/daily/` — GET with write side effect.
- `profile/<pk>/` + `profil_cr/` — duplicated user data with `Custumer`; create is effectively unreachable.
- Shifts, attendance, notifications, most reports, coupons CRUD/validate, loyalty redeem, restaurant settings — **no automated tests**.

### 18.3 Potentially broken / unsafe (reproduced unless noted)
| Endpoint | Problem |
|---|---|
| `POST /api/orders/`, `PATCH /api/orders/<pk>/` | client-controlled `discount`; foreign `reservation` |
| `POST /api/order-products/`, `PATCH /api/order-products/<pk>/quantity/` | client-controlled `price`; foreign product/variant |
| `POST/PATCH /api/delivery/orders/…` | arbitrary/negative `delivery_price` |
| `PATCH /api/orders/<pk>/assign-table/` | cross-restaurant table |
| `PATCH /api/orders/<pk>/status/` | any → any transition |
| `PATCH /api/auth/me/` | plaintext password storage |
| `POST /api/auth/change-password/` | locks account when `new_password` omitted |
| `PATCH /api/filials/<pk>/` | move filial into foreign restaurant |
| `DELETE /api/reviews/<pk>/` | cross-restaurant deletion |
| `POST/DELETE /api/staff/…` | owner's global role overwritten |
| `POST /api/admin/restaurants/<pk>/<action>/` | unknown action deactivates |
| `POST /api/reservations/` | past dates accepted |
| `POST /api/profil_cr/` | always 400 for normally registered users [CODE] |
| Detail updates of settings/ingredients/suppliers/coupons/expenses/kitchens/shifts/delivery staff | FK reassignment not re-validated [CODE] |

### 18.4 Features without an API
- Remove order item; order-item extras/modifiers.
- Public restaurant/filial discovery without login; restaurant `is_active` in public payload.
- Realtime (WebSocket/SSE) for orders, kitchen, delivery.
- Real payment provider callbacks/webhooks; idempotency keys.
- Password reset / email or phone verification / OTP.
- User listing/search for owners (to pick staff/couriers by phone) — currently requires raw user id.
- Multilingual content (tg/ru/en) for menu and restaurant data.
- Image thumbnails / media management.
- Report export (CSV/PDF).
- Super-admin management of users, subscriptions and subscription payments (only restaurants/stats exist).
- Table layout / floor plan (no coordinates or zones on `Stol`).
- Push / SMS / email notifications.
