FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# pg_dump للنسخ الاحتياطي على PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists

COPY . .

# تشغيل غير-root + فحص صحة
RUN useradd -m botuser && mkdir -p /app/backups && chown -R botuser:botuser /app
USER botuser

CMD ["python", "bot.py"]
