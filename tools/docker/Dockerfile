FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Run application as non-root user.
RUN groupadd --gid 1000 finance \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/sh finance \
    && mkdir -p /config /backups \
    && chown -R finance:finance /app /config /backups

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend backend
COPY frontend frontend
RUN chown -R finance:finance /app

EXPOSE 5000

USER finance

CMD ["sh", "-c", "cd backend && python startup.py && exec gunicorn -c gunicorn_conf.py --bind 0.0.0.0:5000 --workers ${GUNICORN_WORKERS:-2} --threads ${GUNICORN_THREADS:-4} --timeout ${GUNICORN_TIMEOUT:-120} app:app"]
