FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home restora && mkdir -p /app/media /app/staticfiles && chown -R restora /app
USER restora

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn server.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile -"]
