FROM python:3.11-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/app/wheels -r requirements.txt


FROM python:3.11-slim-bookworm AS final

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.settings

RUN addgroup --system app && adduser --system --group app

RUN mkdir -p /home/app/web/static && mkdir -p /home/app/web/media
RUN chown -R app:app /home/app/web
WORKDIR /home/app/web

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY . .

RUN chown -R app:app /home/app/web

USER app

EXPOSE 8000

CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:8000", "core.wsgi:application"]
