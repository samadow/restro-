# RESTORA — Technical Specification (ТЗ)

**Версия:** 1.0  
**Тип проекта:** SaaS-платформа для управления ресторанами  
**Backend:** Python, Django, Django REST Framework  
**Database:** PostgreSQL  
**Authentication:** JWT  
**API Documentation:** Swagger / OpenAPI  
**Frontend:** React + TypeScript  
**Цель:** сохтани системаи ягона барои идоракунии ресторанҳо, филиалҳо, меню, брон, заказ, ошхона, пардохт ва молия.

---

## 1. Мақсади проект

Restora — платформаест, ки ба ресторанҳо имкон медиҳад тамоми фаъолияти худро аз як система идора кунанд.

Система бояд барои як ресторан ё шабакаи ресторанҳо кор кунад. Ҳар ресторан маълумот, филиалҳо, кормандон, меню, заказҳо ва ҳисоботи шахсии худро дорад.

Мизоҷ метавонад ресторанро интихоб кунад, менюро бинад, стол брон кунад, заказ диҳад ва ҳолати заказро пайгирӣ намояд.

Роҳбари ресторан метавонад фурӯш, хароҷот, фаъолияти кормандон ва маҳсулоти складро назорат кунад.

### Принсипҳои асосӣ

- Ҳар ресторан танҳо ба маълумоти иҷозатдодашудаи худ дастрасӣ дорад.
- Ҳар филиал кормандон, столҳо ва фаъолияти худро дорад.
- Ҳар заказ аз як ё якчанд маҳсулот иборат аст.
- Ҳар тағйироти муҳими заказ дар система сабт мешавад.
- Пул ва нархҳо бо `DecimalField` нигоҳ дошта мешаванд.
- Ҳамаи амалҳои муҳим дар Backend санҷида мешаванд, на танҳо дар Frontend.

---

## 2. Технологияҳо

### Backend

- Python
- Django
- Django REST Framework
- PostgreSQL
- SimpleJWT
- django-filter
- drf-spectacular барои Swagger/OpenAPI
- Pillow барои тасвирҳо
- Redis ва Django Channels барои вазифаҳои realtime дар марҳилаи баъдӣ
- Celery барои вазифаҳои фонӣ дар марҳилаи баъдӣ

### Frontend

- React
- TypeScript
- Axios ё fetch барои API
- Интерфейси responsive барои телефон, планшет ва компютер

### Deployment

- Ubuntu Server
- Gunicorn
- Nginx
- HTTPS
- Environment variables барои паролҳо ва калидҳои махфӣ
- Docker барои муҳити deployment, агар лозим шавад

---

## 3. Рольҳои истифодабарандагон

### 3.1. Super Admin

Администратори тамоми платформа.

Функсияҳо:

- Дидани ҳамаи ресторанҳои ба система пайвастшуда.
- Бастан ё фаъол кардани ресторан.
- Идора кардани тарифҳо ва подпискаҳо.
- Дидани ҳолати пардохтҳои подписка.
- Идора кардани истифодабарандагон.
- Дидани логҳои амниятӣ.
- Дидани омори умумии платформа.

Super Admin бояд бо Owner-и ресторан як роль набошад.

### 3.2. Restaurant Owner

Соҳиби ресторан.

Функсияҳо:

- Идора кардани маълумоти ресторан.
- Сохтан ва тағйир додани филиалҳо.
- Илова кардани Manager ва кормандон.
- Идора кардани меню ва нархҳо.
- Дидани ҳамаи заказҳои ресторан.
- Дидани пардохтҳо, даромад ва хароҷот.
- Идора кардани склад.
- Дидани ҳисоботҳо.
- Идора кардани подписка.

### 3.3. Manager

Менеҷери филиал ё ресторан.

Функсияҳо:

- Идора кардани столҳо ва бронҳо.
- Идора кардани заказҳо.
- Назорат кардани кормандон.
- Дидани ҳисоботи иҷозатдодашуда.
- Идора кардани маҳсулот ва дастрасии онҳо.
- Назорат кардани кори ошхона.

Manager набояд ҳуқуқи Super Admin дошта бошад.

### 3.4. Waiter

Пешхизмат.

Функсияҳо:

- Дидани столҳои филиали худ.
- Сохтани заказ барои стол.
- Илова кардани маҳсулот ба заказ.
- Тағйир додани миқдори маҳсулот.
- Ирсол кардани заказ ба ошхона.
- Дидани ҳолати тайёршавии заказ.
- Дидани заказҳои ба ӯ иҷозатдодашуда.

Waiter набояд тавонад нархи маҳсулотро худсарона тағйир диҳад ё заказҳои дигар филиалро идора кунад.

### 3.5. Chef

Ошпаз ё корманди ошхона.

Функсияҳо:

- Дидани заказҳои ба ошхона фиристодашуда.
- Дидани рӯйхати маҳсулоти заказ.
- Гузоштани статуси `preparing`.
- Гузоштани статуси `ready`.
- Дидани вақти қабул ва тайёр кардани заказ.

Chef набояд маълумоти махфии молиявии ресторанро бинад.

### 3.6. Cashier

Кассир.

Функсияҳо:

- Дидани заказҳои барои пардохт тайёр.
- Сабти пардохти нақдӣ.
- Дидани маблағи пардохтшуда ва боқимонда.
- Сохтани чек ё сабти амалиёти пардохт.
- Сабти баргардонидани пул бо иҷозати дахлдор.

### 3.7. Customer

Мизоҷ.

Функсияҳо:

- Регистрация ва Login.
- Дидани ресторанҳо ва филиалҳо.
- Дидани меню ва нархҳо.
- Брон кардани стол.
- Сохтани заказ.
- Дидани таърихи заказҳо.
- Пардохти онлайн, агар провайдер пайваст шуда бошад.
- Додани рейтинг ва отзыв.
- Дидани уведомления.
- Идора кардани маълумоти шахсӣ.

### 3.8. Delivery Staff

Корманди расонидани заказ.

Функсияҳо:

- Дидани заказҳои ба ӯ таъиншуда.
- Дидани суроға ва рақами телефони зарурӣ.
- Тағйир додани статуси расонидан.
- Сабти вақти супоридани заказ.

---

## 4. Модулҳои асосии система

### 4.1. Accounts

Моделҳо:

- `Custumer`
- `Staff`
- `CustomerAddress`

Функсияҳои зарурӣ:

- `register()` — регистрация.
- `login()` — гирифтани JWT token.
- `refresh_token()` — нав кардани access token.
- `logout()` — бекор кардани refresh token, агар blacklist истифода шавад.
- `get_me()` — маълумоти корбари ҳозира.
- `update_me()` — тағйир додани профил.
- `change_password()` — тағйир додани парол.
- `reset_password()` — барқарор кардани парол тавассути механизми тасдиқ.
- `upload_avatar()` — бор кардани расми профил.

Қоидаҳо:

- Email ё username бояд мувофиқи сиёсати регистрация санҷида шавад.
- Парол бо механизми стандартии Django нигоҳ дошта шавад.
- Истифодабаранда набояд аз API ҳуқуқи худро ба `super_admin` ё Owner-и беиҷозат иваз карда тавонад.
- Маълумоти шахсӣ танҳо ба соҳиби аккаунт ва шахсони иҷозатдошта намоён бошад.

### 4.2. Restaurant ва Filial

Моделҳо:

- `Restaurant`
- `filial`
- `RestaurantSettings`
- `Stol`

Функсияҳо:

- `create_restaurant()` — сохтани ресторан.
- `update_restaurant()` — тағйир додани маълумот.
- `list_restaurants()` — рӯйхати ресторанҳои дастрас.
- `create_filial()` — сохтани филиал.
- `update_filial()` — тағйир додани филиал.
- `list_filials()` — рӯйхати филиалҳо.
- `create_stol()` — сохтани стол.
- `update_stol()` — тағйир додани стол.
- `list_stols()` — рӯйхати столҳои филиал.
- `update_restaurant_settings()` — тағйир додани танзимот.

Қоидаҳо:

- Ҳар филиал бояд ба як ресторан тааллуқ дошта бошад.
- Ҳар стол бояд ба як филиал тааллуқ дошта бошад.
- Ҳамаи объектҳо бояд аз рӯйи ҳуқуқи корбар филтр карда шаванд.
- Ресторан набояд филиали ресторани дигарро идора кунад.

### 4.3. Menu

Моделҳо:

- `Category`
- `Product`
- `ProductVariant`
- `ProductExtra`

Функсияҳо:

- `create_category()`
- `update_category()`
- `delete_category()`
- `list_categories()`
- `create_product()`
- `update_product()`
- `delete_product()`
- `list_products()`
- `filter_products()`
- `search_products()`
- `update_product_availability()`
- `create_product_variant()`
- `create_product_extra()`

Филтрҳо:

- Аз рӯйи категория.
- Аз рӯйи нарх.
- Аз рӯйи номи маҳсулот.
- Аз рӯйи дастрас будан.
- Аз рӯйи ресторан ё филиал.

Қоидаҳо:

- Нарх бояд мусбат бошад.
- Маҳсулоти дастнорас ба закази нав илова карда нашавад.
- Мизоҷ набояд нархи маҳсулотро аз Frontend муайян кунад.
- Агар маҳсулот аллакай дар заказҳои гузашта истифода шуда бошад, нест кардани он набояд таърихи заказро вайрон кунад.

### 4.4. Reservation

Модел:

- `dron_stol`

Функсияҳо:

- `create_reservation()`
- `list_reservations()`
- `get_reservation_detail()`
- `update_reservation()`
- `cancel_reservation()`
- `confirm_reservation()`
- `check_table_availability()`

Маълумоти брон:

- Мизоҷ.
- Ресторан.
- Филиал.
- Стол.
- Сана.
- Вақти оғоз.
- Вақти анҷом.
- Шумораи меҳмонон.
- Статус.
- Шарҳ.

Статусҳо:

- `pending`
- `confirmed`
- `cancelled`
- `completed`
- `rejected`

Қоидаҳо:

- Стол дар як вақт набояд барои ду брон тасдиқ шавад.
- Шумораи меҳмонон набояд аз ғунҷоиши стол зиёд бошад.
- Вақти анҷом бояд аз вақти оғоз дертар бошад.
- Ҳангоми бекор кардани брон, сабаби бекоркунӣ нигоҳ дошта шавад.
- Санҷиши брон бояд дар Backend иҷро шавад, то бронҳои ҳамзамон конфликт насозанд.

### 4.5. Orders

Моделҳо:

- `Order`
- `dron_product`
- `OrderStatusHistory`
- `Coupon`

Функсияҳо:

- `create_order()` — сохтани заказ.
- `add_order_item()` — илова кардани маҳсулот.
- `update_order_item()` — тағйир додани миқдор.
- `remove_order_item()` — нест кардани маҳсулот аз заказ.
- `calculate_order_total()` — ҳисоб кардани маблағ.
- `apply_coupon()` — истифодаи купон.
- `submit_order()` — тасдиқ ва фиристодани заказ.
- `cancel_order()` — бекор кардани заказ.
- `list_orders()` — рӯйхати заказҳо.
- `get_order_detail()` — маълумоти пурраи заказ.
- `update_order_status()` — тағйир додани статус.
- `get_my_orders()` — таърихи заказҳои мизоҷ.

Статусҳои заказ:

- `pending`
- `confirmed`
- `preparing`
- `ready`
- `served`
- `completed`
- `cancelled`

Қоидаҳо:

- Ҳар заказ рақами ягона дошта бошад.
- Маблағи заказ аз нархи маҳсулот, миқдор, скидка ва хароҷоти дахлдор ҳисоб карда шавад.
- Сервер маблағро ҳисоб мекунад; Frontend маблағи ниҳоиро дикта намекунад.
- Ҳангоми илова шудани маҳсулот, нархи он дар `dron_product` ҳамчун нархи вақти заказ нигоҳ дошта шавад.
- Закази пардохтшуда набояд бе иҷозат тағйир дода шавад.
- Тағйироти статус дар `OrderStatusHistory` сабт шавад.
- Закази як ресторан набояд маҳсулоти ресторани дигарро дар бар гирад.

### 4.6. Kitchen

Моделҳо:

- `Kitchen`
- `KitchenOrder`
- `KitchenOrderItem`

Функсияҳо:

- `send_order_to_kitchen()`
- `list_kitchen_orders()`
- `get_kitchen_order_detail()`
- `start_preparation()`
- `mark_item_ready()`
- `mark_order_ready()`

Қоидаҳо:

- Ошхона танҳо заказҳои филиали дахлдорро мебинад.
- Вақти оғози тайёркунӣ ва анҷоми он сабт мешавад.
- Закази тайёршуда ба Waiter ё Customer нишон дода мешавад.
- Тағйироти муҳим бояд бо вақт ва корбари иҷрокунанда сабт шавад.

### 4.7. Payments

Моделҳо:

- `Payment`
- `Refund`

Функсияҳо:

- `create_payment()`
- `confirm_payment()`
- `get_payment_detail()`
- `list_payments()`
- `create_refund()`
- `get_order_payment_status()`

Усулҳои пардохт:

- `cash`
- `card`
- `online`
- `other`

Статусҳо:

- `pending`
- `paid`
- `failed`
- `cancelled`
- `refunded`

Қоидаҳо:

- Пардохт бояд ба закази дуруст пайваст бошад.
- Суммаи пардохт набояд бе санҷиш аз маблағи боқимонда зиёд шавад.
- Барои пардохти онлайн бояд провайдери пардохт пайваст карда шавад.
- Статуси пардохти онлайн танҳо аз ҷавоби тасдиқшудаи провайдер ё webhook-и санҷидашуда тағйир дода шавад.
- Амалиёти баргардонидани пул бояд ҳуқуқи махсус дошта бошад.
- Рақами транзаксия барои санҷиш ва пешгирӣ кардани такрори пардохт нигоҳ дошта шавад.

### 4.8. Inventory

Моделҳо:

- `Ingredient`
- `ProductIngredient`
- `Supplier`
- `StockMovement`

Функсияҳо:

- `create_ingredient()`
- `update_ingredient()`
- `list_ingredients()`
- `add_stock()`
- `remove_stock()`
- `transfer_stock()`
- `get_stock_balance()`
- `get_low_stock_products()`
- `list_stock_movements()`
- `create_supplier()`

Қоидаҳо:

- Ҳар ингредиент бояд воҳиди ченак дошта бошад.
- Ҳаракати склад бояд сабт шавад.
- Миқдори склад набояд тасодуфан манфӣ шавад.
- Ҳангоми қабул кардани маҳсулот миқдор зиёд мешавад.
- Ҳангоми сарф ё истифода миқдор кам мешавад.
- Барои тағйироти склад сабаб ва корбари иҷрокунанда нигоҳ дошта шавад.

### 4.9. Staff

Моделҳо:

- `Staff`
- `StaffShift`
- `StaffAttendance`

Функсияҳо:

- `create_staff()`
- `update_staff()`
- `deactivate_staff()`
- `list_staff()`
- `assign_staff_role()`
- `start_shift()`
- `end_shift()`
- `check_in()`
- `check_out()`
- `get_staff_attendance()`

Қоидаҳо:

- Корманд бояд ба ресторан ва филиали муайян вобаста бошад.
- Корманди ғайрифаъол набояд ба система ҳамчун корманди фаъол амал кунад.
- Смена ва ҳозиршавӣ бояд сана ва вақт дошта бошанд.
- Дастрасии ҳар корманд аз рӯйи роль ва иҷозатҳо муайян карда шавад.

### 4.10. Customer

Моделҳо:

- `CustomerAddress`
- `CustomerFavorite`
- `Review`

Функсияҳо:

- `add_address()`
- `update_address()`
- `delete_address()`
- `add_favorite()`
- `remove_favorite()`
- `list_favorites()`
- `create_review()`
- `update_review()`
- `list_restaurant_reviews()`

Қоидаҳо:

- Мизоҷ танҳо суроғаҳо ва маълумоти шахсии худро идора мекунад.
- Рейтинг бояд дар ҳудуди 1 то 5 бошад.
- Агар танҳо мизоҷони воқеан заказкарда отзыв дода тавонанд, ин бояд дар Backend санҷида шавад.
- Як заказ набояд барои як ресторан чанд маротиба отзыв гирад, агар чунин имконият махсус пешбинӣ нашуда бошад.

### 4.11. Notifications

Моделҳо:

- `Notification`
- `RestaurantNotification`

Функсияҳо:

- `create_notification()`
- `list_notifications()`
- `mark_notification_read()`
- `mark_all_notifications_read()`
- `delete_notification()`

Уведомления метавонанд барои ин ҳолатҳо фиристода шаванд:

- Заказ қабул шуд.
- Заказ ба ошхона фиристода шуд.
- Заказ тайёр шуд.
- Брон тасдиқ ё бекор шуд.
- Пардохт тасдиқ шуд.
- Миқдори склад кам шуд.
- Подписка ба охир расида истодааст.

Дар версияи аввал уведомления метавонанд дар дохили система бошанд. Email, SMS ва push notification дар марҳилаи баъдӣ илова мешаванд.

### 4.12. Delivery

Моделҳо:

- `Delivery`
- `DeliveryStaff`

Функсияҳо:

- `create_delivery()`
- `assign_delivery_staff()`
- `list_my_deliveries()`
- `update_delivery_status()`
- `complete_delivery()`

Статусҳо:

- `pending`
- `assigned`
- `picked_up`
- `delivering`
- `delivered`
- `cancelled`

Қоидаҳо:

- Delivery бояд ба як заказ вобаста бошад.
- Корманди расондан танҳо заказҳои ба ӯ таъиншударо бинад.
- Суроға, рақами телефон ва вақти расондан нигоҳ дошта шаванд.

### 4.13. Reports ва Expenses

Моделҳо:

- `DailyReport`
- `Expense`

Функсияҳо:

- `get_daily_report()`
- `get_monthly_report()`
- `get_sales_report()`
- `get_order_statistics()`
- `get_product_statistics()`
- `create_expense()`
- `update_expense()`
- `list_expenses()`

Ҳисоботҳо бояд нишон диҳанд:

- Шумораи заказҳо.
- Маблағи умумии фурӯш.
- Маблағи воқеан пардохтшуда.
- Заказҳои бекоршуда.
- Маҳсулоти серхаридор.
- Хароҷот.
- Фарқи фурӯш ва хароҷот.

Муҳим: фурӯш, пардохт ва фоида як чиз нестанд. Формулаи ҳисобот бояд дақиқ муайян шавад. `DailyReport` метавонад ҳамчун натиҷаи ҳисобкунии Backend сохта шавад; он набояд бе назорат рақамҳои нодуруст нигоҳ дорад.

### 4.14. Subscription

Моделҳо:

- `SubscriptionPlan`
- `RestaurantSubscription`
- `SubscriptionPayment`

Функсияҳо:

- `create_subscription_plan()`
- `list_subscription_plans()`
- `subscribe_restaurant()`
- `renew_subscription()`
- `cancel_subscription()`
- `check_subscription_status()`
- `list_subscription_payments()`

Қоидаҳо:

- Ҳар подписка ба як ресторан тааллуқ дорад.
- Подписка санаи оғоз ва анҷом дорад.
- Маҳдудияти филиалҳо ва кормандон аз рӯйи тариф санҷида шавад.
- Баъд аз анҷоми подписка система бояд мувофиқи сиёсати муайяншуда амал кунад: масалан, иҷозати тамошои маълумотро нигоҳ дошта, сохтани объектҳои навро маҳдуд кунад.

### 4.15. Loyalty

Моделҳо:

- `LoyaltyAccount`
- `LoyaltyTransaction`

Функсияҳо:

- `get_loyalty_balance()`
- `add_loyalty_points()`
- `use_loyalty_points()`
- `list_loyalty_transactions()`

Қоидаҳо:

- Ҳар тағйироти холҳо дар `LoyaltyTransaction` сабт шавад.
- Холҳо танҳо аз рӯйи қоидаи муайяншуда ҳисоб карда шаванд.
- Як заказ набояд ду маротиба хол диҳад.
- Ҳангоми бекор ё баргардонидани заказ холҳои мувофиқ ислоҳ карда шаванд.

### 4.16. AuditLog

Модел:

- `AuditLog`

Функсияҳо:

- `create_audit_log()`
- `list_audit_logs()`
- `get_audit_log_detail()`

Дар логҳо сабт мешаванд:

- Кӣ амалро иҷро кард.
- Кадом объект тағйир ёфт.
- Навъи амал.
- Вақти иҷро.
- Тавсифи тағйирот.

AuditLog бояд барои Owner ва Super Admin мувофиқи ҳуқуқ дастрас бошад. Логҳои амниятӣ набояд ба корбари одӣ таҳриршаванда бошанд.

---

## 5. API Endpoints

Ҳамаи API-ҳо бояд зери `/api/v1/` бошанд.

### Accounts

- `POST /api/v1/accounts/register/`
- `POST /api/v1/accounts/login/`
- `POST /api/v1/accounts/token/refresh/`
- `POST /api/v1/accounts/logout/`
- `GET /api/v1/accounts/me/`
- `PATCH /api/v1/accounts/me/`
- `POST /api/v1/accounts/change-password/`

### Restaurants ва Filials

- `GET /api/v1/restaurants/`
- `POST /api/v1/restaurants/`
- `GET /api/v1/restaurants/{id}/`
- `PATCH /api/v1/restaurants/{id}/`
- `GET /api/v1/filials/`
- `POST /api/v1/filials/`
- `GET /api/v1/filials/{id}/`
- `PATCH /api/v1/filials/{id}/`
- `GET /api/v1/filials/{id}/tables/`

### Menu

- `GET /api/v1/categories/`
- `POST /api/v1/categories/`
- `PATCH /api/v1/categories/{id}/`
- `DELETE /api/v1/categories/{id}/`
- `GET /api/v1/products/`
- `POST /api/v1/products/`
- `GET /api/v1/products/{id}/`
- `PATCH /api/v1/products/{id}/`
- `DELETE /api/v1/products/{id}/`

Филтрҳои маҳсулот:

- `?category=1`
- `?min_price=10`
- `?max_price=100`
- `?search=burger`
- `?is_available=true`

### Reservation

- `GET /api/v1/reservations/`
- `POST /api/v1/reservations/`
- `GET /api/v1/reservations/{id}/`
- `PATCH /api/v1/reservations/{id}/`
- `POST /api/v1/reservations/{id}/cancel/`
- `POST /api/v1/reservations/{id}/confirm/`
- `GET /api/v1/filials/{id}/availability/`

### Orders

- `GET /api/v1/orders/`
- `POST /api/v1/orders/`
- `GET /api/v1/orders/{id}/`
- `PATCH /api/v1/orders/{id}/`
- `POST /api/v1/orders/{id}/submit/`
- `POST /api/v1/orders/{id}/cancel/`
- `POST /api/v1/orders/{id}/status/`
- `GET /api/v1/my-orders/`

### Kitchen

- `GET /api/v1/kitchen/orders/`
- `GET /api/v1/kitchen/orders/{id}/`
- `POST /api/v1/kitchen/orders/{id}/start/`
- `POST /api/v1/kitchen/orders/{id}/ready/`

### Payments

- `GET /api/v1/payments/`
- `POST /api/v1/payments/`
- `GET /api/v1/payments/{id}/`
- `POST /api/v1/payments/{id}/refund/`

### Inventory

- `GET /api/v1/inventory/ingredients/`
- `POST /api/v1/inventory/ingredients/`
- `PATCH /api/v1/inventory/ingredients/{id}/`
- `GET /api/v1/inventory/movements/`
- `POST /api/v1/inventory/movements/`
- `GET /api/v1/inventory/low-stock/`
- `GET /api/v1/inventory/suppliers/`
- `POST /api/v1/inventory/suppliers/`

### Staff

- `GET /api/v1/staff/`
- `POST /api/v1/staff/`
- `GET /api/v1/staff/{id}/`
- `PATCH /api/v1/staff/{id}/`
- `POST /api/v1/staff/{id}/deactivate/`
- `POST /api/v1/staff/shifts/start/`
- `POST /api/v1/staff/shifts/end/`
- `GET /api/v1/staff/attendance/`

### Reviews ва Notifications

- `GET /api/v1/reviews/`
- `POST /api/v1/reviews/`
- `GET /api/v1/notifications/`
- `POST /api/v1/notifications/{id}/read/`

### Reports

- `GET /api/v1/reports/daily/`
- `GET /api/v1/reports/monthly/`
- `GET /api/v1/reports/sales/`
- `GET /api/v1/reports/products/`
- `GET /api/v1/reports/expenses/`
- `POST /api/v1/reports/expenses/`

### Subscription

- `GET /api/v1/subscriptions/plans/`
- `GET /api/v1/subscriptions/current/`
- `POST /api/v1/subscriptions/subscribe/`
- `POST /api/v1/subscriptions/renew/`
- `GET /api/v1/subscriptions/payments/`

Ин endpoint-ҳо талаботи функсионалӣ мебошанд. Ҳангоми реализация номҳо ва сохтори дақиқи endpoint-ҳо бояд дар `urls.py` ва Swagger яксон нигоҳ дошта шаванд.

---

## 6. Django структураи проект

Структураи тавсияшаванда:

```text
restora/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
├── restaurants/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
├── menu/
├── reservations/
├── orders/
├── kitchen/
├── payments/
├── inventory/
├── staff/
├── customers/
├── notifications/
├── reports/
├── subscriptions/
├── reviews/
└── requirements.txt
```

Барои проекте, ки калон мешавад, ҳамаи моделҳоро дар як app нигоҳ доштан тавсия намешавад. Моделҳои Accounts, Orders, Menu ва дигар модулҳо бояд дар app-ҳои мувофиқ ҷойгир шаванд.

Номҳои моделҳои мавҷудаи `Custumer`, `filial`, `Stol`, `dron_stol` ва `dron_product` метавонанд дар версияи аввал нигоҳ дошта шаванд. Барои версияи production беҳтар аст номҳои стандартӣ ба мисли `Customer`, `Branch`, `Table`, `Reservation` ва `OrderItem` истифода шаванд.

---

## 7. Serializers

Барои ҳар модели API-дастрас бояд Serializer сохта шавад.

Намунаи вазифаҳо:

- `RegisterSerializer`
- `UserSerializer`
- `RestaurantSerializer`
- `FilialSerializer`
- `StolSerializer`
- `CategorySerializer`
- `ProductSerializer`
- `ReservationSerializer`
- `OrderSerializer`
- `OrderItemSerializer`
- `PaymentSerializer`
- `IngredientSerializer`
- `StaffSerializer`
- `ReviewSerializer`

Serializer бояд:

- Маълумоти воридшударо санҷад.
- Field-ҳои иҷозатдодашударо муайян кунад.
- Маблағи заказро аз маълумоти боварибахши база ҳисоб кунад.
- Маълумоти махфиро нишон надиҳад.
- FK-ҳоро аз рӯйи ҳуқуқи корбар санҷад.
- Барои объектҳои вобаста validation иҷро кунад.

---

## 8. Views ва Business Logic

Барои CRUD-и одӣ аз `ModelViewSet` ё Generic Views истифода бурдан мумкин аст.

Барои амалҳои махсус endpoint ё action сохта мешавад:

- Сохтани заказ.
- Тасдиқи брон.
- Ирсол ба ошхона.
- Тасдиқи пардохт.
- Баргардонидани пул.
- Илова ва кам кардани склад.
- Ҳисоб кардани отчет.

Мантиқи муҳимро дар Serializer ё Service Layer нигоҳ доштан мумкин аст. Масалан:

- `services/order_service.py`
- `services/payment_service.py`
- `services/inventory_service.py`
- `services/reservation_service.py`

Ҳар амалиёт бояд validation, permission ва санҷиши робитаи объектҳоро дошта бошад.

---

## 9. Permissions ва Security

Система бояд аз дастрасии ғайриқонунӣ муҳофизат шавад.

Талабот:

- JWT authentication.
- Role-based permissions.
- Филтр кардани маълумот аз рӯйи restaurant ва filial.
- Санҷидани ҳуқуқи Owner пеш аз тағйир додани ресторан.
- Санҷидани ҳуқуқи Waiter пеш аз тағйир додани заказ.
- Санҷидани ҳуқуқи Chef барои амалҳои ошхона.
- Маҳдуд кардани endpoint-ҳои пардохт.
- Validation барои ҳамаи input-ҳо.
- Нигоҳ доштани secret key ва database password дар environment variables.
- Истифодаи HTTPS дар production.
- Rate limiting барои endpoint-ҳои ҳассос, аз ҷумла login.
- Пешгирӣ аз дубора иҷро шудани пардохт ва заказ.
- Санҷиши upload-и файлҳо ва тасвирҳо.

Муҳим: танҳо пинҳон кардани тугма дар Frontend амният нест. Ҳамаи ҳуқуқҳо бояд дар Backend санҷида шаванд.

---

## 10. Database ва Integrity

Талабот:

- PostgreSQL ҳамчун базаи асосӣ.
- ForeignKey ва OneToOneField барои муносибатҳои дуруст.
- `DecimalField` барои маблағ.
- `DateField`, `TimeField` ва `DateTimeField` барои сана ва вақт.
- `PositiveIntegerField` ё validation барои миқдор.
- `UniqueConstraint` барои қиматҳои воқеан ягона.
- `transaction.atomic()` барои амалиётҳои молиявӣ ва склад.
- Индексҳо барои филтрҳои зуд-зуд истифодашаванда.
- Санҷиши duplicate reservation ва duplicate payment.

Барои нархи маҳсулот дар заказ нархи вақти харид нигоҳ дошта шавад. Агар Owner баъдтар нархро иваз кунад, таърихи заказҳои гузашта бояд тағйир наёбад.

---

## 11. Frontend

Frontend бояд панелҳои зеринро дошта бошад:

### Customer Interface

- Регистрация ва Login.
- Рӯйхати ресторанҳо.
- Интихоби филиал.
- Меню ва ҷустуҷӯи маҳсулот.
- Сабади харид.
- Брон кардани стол.
- Таърихи заказҳо.
- Статуси заказ.
- Профил ва адресҳо.
- Рейтинг ва отзыв.

### Restaurant Dashboard

- Dashboard бо омор.
- Идора кардани филиалҳо.
- Идора кардани столҳо.
- Идора кардани категория ва маҳсулот.
- Идора кардани заказҳо.
- Бронҳо.
- Кормандон ва рольҳо.
- Склад ва ингредиентҳо.
- Пардохтҳо ва хароҷот.
- Отчетҳо.
- Танзимоти ресторан ва подписка.

### Kitchen Dashboard

- Заказҳои нав.
- Заказҳои дар ҳоли тайёршавӣ.
- Заказҳои тайёршуда.
- Вақти тайёркунӣ.
- Тағйир додани статус.

### Super Admin Dashboard

- Ресторанҳо.
- Истифодабарандагон.
- Тарифҳо.
- Подпискаҳо.
- Пардохтҳои подписка.
- Audit logs.

---

## 12. Testing

Барои ҳар модул бояд тестҳо сохта шаванд.

Тестҳои ҳатмӣ:

- Регистрация ва Login.
- JWT authentication.
- Permissions барои ҳар роль.
- Дастрас набудани маълумоти ресторани дигар.
- Сохтани филиал ва стол.
- Validation-и маҳсулот ва нарх.
- Бронҳои конфликткунанда.
- Сохтани заказ ва ҳисобкунии маблағ.
- Тағйир додани статуси заказ.
- Пардохти такрорӣ.
- Баргардонидани пул.
- Каму зиёд шудани склад.
- Тестҳои подписка ва маҳдудиятҳо.
- Тестҳои API барои endpoint-ҳои асосӣ.

Барои тестҳо Django TestCase ё pytest истифода бурдан мумкин аст.

---

## 13. Swagger ва API Documentation

Ҳамаи endpoint-ҳо бояд дар Swagger ҳуҷҷатгузорӣ шаванд.

Талабот:

- Номи endpoint.
- Method: GET, POST, PATCH, DELETE.
- Request body.
- Response body.
- Validation errors.
- Authentication requirements.
- Status codes.
- Намунаҳои маълумоти воридшаванда.

Endpoint-ҳои documentation, масалан:

- `/api/schema/`
- `/api/docs/`

Номи ниҳоӣ мувофиқи конфигуратсияи `drf-spectacular` муайян карда мешавад.

---

## 14. Deployment

Дар production бояд:

- PostgreSQL дуруст танзим шавад.
- `DEBUG=False` бошад.
- `ALLOWED_HOSTS` танзим шавад.
- `SECRET_KEY` дар environment нигоҳ дошта шавад.
- Static ва media files дуруст хизматрасонӣ шаванд.
- HTTPS фаъол бошад.
- Database backup ташкил карда шавад.
- Log-ҳои хатогиҳо сабт шаванд.
- Миграцияҳо пеш аз deployment санҷида шаванд.
- Endpoint-ҳои муҳим баъд аз deployment санҷида шаванд.

---

## 15. Марҳилаҳои иҷрои проект

### Phase 1 — MVP

Аввал инҳоро сохтан лозим аст:

1. Accounts ва JWT.
2. Restaurant ва Filial.
3. Stol ва Reservation.
4. Category ва Product.
5. Order ва OrderItem.
6. Order Status.
7. Payment-и одӣ, аввал нақдӣ.
8. Role-based permissions.
9. Swagger.
10. Тестҳои асосӣ.

### Phase 2 — Restaurant Operations

1. Kitchen Dashboard.
2. Staff ва StaffShift.
3. Inventory.
4. Supplier ва StockMovement.
5. Reports ва Expenses.
6. Notifications.
7. Customer Reviews.

### Phase 3 — SaaS ва Advanced Features

1. Subscription Plans.
2. Subscription Payments.
3. Delivery.
4. Coupon ва Discounts.
5. Loyalty Points.
6. Audit Logs.
7. Realtime status updates.
8. Online payment integration.
9. Advanced analytics.

### Phase 4 — Production

1. Амният ва санҷиши permissions.
2. Optimization-и database.
3. Backup ва logging.
4. Deployment.
5. Load testing.
6. Monitoring ва error tracking.

---

## 16. Меъёрҳои қабул (Acceptance Criteria)

Проект вақте барои MVP тайёр ҳисобида мешавад, ки:

- Корбар регистрация ва Login карда тавонад.
- Owner ресторан ва филиал созад.
- Owner категория ва маҳсулот илова карда тавонад.
- Мизоҷ менюро бинад ва заказ созад.
- Заказ аз рӯйи нархи база ҳисоб карда шавад.
- Waiter заказро ба ошхона фиристад.
- Chef статуси заказро тағйир диҳад.
- Cashier пардохтро сабт карда тавонад.
- Бронҳои як стол барои як вақт конфликт накунанд.
- Корманди ресторан ба маълумоти ресторани дигар дастрасӣ надошта бошад.
- API-ҳо дар Swagger нишон дода шаванд.
- Тестҳои асосӣ гузаранд.
- Проект дар муҳити deployment кор кунад.

---

## 17. Қоидаҳои муҳим барои таҳиягар

1. Аввал MVP сохта шавад; ҳамаи модулҳоро якбора навиштан лозим нест.
2. Ҳар app вазифаи муайян дошта бошад.
3. Ҳар endpoint permission ва validation дошта бошад.
4. Ҳеҷ гоҳ маблағи пардохтро танҳо аз маълумоти Frontend қабул накун.
5. Барои амалиётҳои молиявӣ transaction ва санҷиши дубора иҷро шуданро истифода бар.
6. Маълумоти ресторанҳо аз ҳамдигар ҷудо нигоҳ дошта шавад.
7. Пеш аз тағйир додани User model бояд `AUTH_USER_MODEL` дуруст танзим карда шавад.
8. Барои ҳар модели нав migration ва тест иҷро шавад.
9. Ҳар марҳила дар Git commit карда шавад.
10. Функсияҳои асосӣ бояд пеш аз илова кардани хусусиятҳои мураккаб кор кунанд.

**Натиҷаи ниҳоӣ:** Restora бояд як платформаи ягона бошад, ки ресторанҳо фаъолияти ҳаррӯзаи худро идора карда, мизоҷон менюро бинанд, брон кунанд ва заказ диҳанд, кормандон вазифаҳои худро иҷро кунанд ва роҳбарият натиҷаҳои молиявиро таҳлил намояд.
