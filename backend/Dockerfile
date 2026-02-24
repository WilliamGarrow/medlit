FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

RUN groupadd -r medlit && useradd -r -g medlit medlit

COPY --from=builder /install /usr/local
WORKDIR /app
COPY app/ ./app/

USER medlit

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
