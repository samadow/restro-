# Restora — deploy (Ubuntu Server + Docker)

## 1. Server
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
git clone <repo> restora && cd restora
cp .env.example .env        # fill SECRET_KEY, DB_PASSWORD, ALLOWED_HOSTS ...
```
New SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 2. HTTPS certificate
Put `fullchain.pem` and `privkey.pem` into `nginx/certs/` (for example from Let's Encrypt / certbot).

## 3. Start
```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```
`migrate` and `collectstatic` run automatically when `web` starts.

- API: `https://<domain>/api/`
- Swagger: `https://<domain>/api/docs/`, ReDoc: `/api/redoc/`, schema: `/api/schema/`

## 4. Every day (cron)
```bash
# subscriptions: expire + "ends soon" notifications
0 6 * * * cd /root/restora && docker compose exec -T web python manage.py check_subscriptions

# database backup
0 3 * * * cd /root/restora && docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backups/restora_$(date +\%F).sql
```
Restore: `cat backups/restora_2026-10-31.sql | docker compose exec -T db psql -U restora restora`

## 5. Logs / monitoring
```bash
docker compose logs -f web      # gunicorn + django logs
docker compose logs -f nginx
docker compose ps
```

## 6. Update
```bash
git pull && docker compose up -d --build
```

## Tests
```bash
python manage.py test myapp
```
