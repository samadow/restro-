# Restora - Restaurant Management SaaS API

Multi-tenant backend API for restaurant chains, built with **Django REST Framework**.
One platform serves many restaurants and branches, with strict tenant isolation and role-based access control.

## Features

- **Authentication:** JWT (access/refresh), registration, profile, role management
- **Roles:** owner, manager, chef, waiter, cashier, delivery, super admin
- **Restaurants and branches:** settings, filials, staff, tables
- **Reservations:** availability check, overlap and capacity validation, status workflow
- **Menu:** categories, products, variants, extras, public menu endpoint with filters
- **Orders:** order items, coupons, loyalty points, status history, table assignment
- **Kitchen:** kitchen tickets (start / ready), automatic ingredient deduction
- **Payments:** cash/card/online (mock gateway), partial payments, refunds
- **Delivery:** couriers, assignment, picked-up / delivered flow
- **Inventory:** ingredients, suppliers, stock movements, low-stock alerts
- **Staff:** shifts and attendance
- **Reports:** daily, sales, products, payments, cancelled orders, expenses
- **SaaS subscriptions:** plans with branch and staff limits
- **Audit log** and super-admin statistics
- **AI endpoints (Groq):** menu assistant, product descriptions, reviews summary, sales insights, inventory forecast

## Tech stack

Python · Django · Django REST Framework · SimpleJWT · drf-spectacular (OpenAPI) · Docker · nginx

## API documentation

When the server is running:

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI schema: `/api/schema/`

The full endpoint reference is in [RESTORA_API_MAP.md](RESTORA_API_MAP.md).

## Getting started

1. Copy `.env.example` to `.env` and fill in the values.
2. Install dependencies: `pip install -r requirements.txt`
3. Apply migrations: `python manage.py migrate`
4. Run the server: `python manage.py runserver`

Docker and production deployment (nginx) are described in [DEPLOY.md](DEPLOY.md).

## Project documents

- [RESTORA_API_MAP.md](RESTORA_API_MAP.md) - endpoint map
- [RESTORA_IMPLEMENTATION_PLAN.md](RESTORA_IMPLEMENTATION_PLAN.md) - implementation plan
- [RESTORA_PROGRESS.md](RESTORA_PROGRESS.md) - progress log
- [RESTORA_PROJECT_AUDIT.md](RESTORA_PROJECT_AUDIT.md) - project audit

## Author

Samadow - Junior Python Backend Developer, Dushanbe, Tajikistan.
[LinkedIn](https://www.linkedin.com/in/samadow-sh-576319435/) · [GitHub](https://github.com/samadow)
