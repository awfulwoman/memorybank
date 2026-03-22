FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM base AS runtime

COPY --from=builder /install /usr/local
COPY . .

ENV DJANGO_SETTINGS_MODULE=memorybank.settings
ENV PYTHONUNBUFFERED=1

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "memorybank.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
