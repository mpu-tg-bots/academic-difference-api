FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache build-base postgresql-dev

WORKDIR /opt/app

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix="/install" -r requirements.txt

COPY . .


FROM python:3.12-alpine

RUN apk update && apk add --no-cache postgresql-libs && rm -rf /var/cache/apk/*

WORKDIR /opt/app

COPY --from=builder /install /usr/local
COPY --from=builder /opt/app .

EXPOSE 8000
