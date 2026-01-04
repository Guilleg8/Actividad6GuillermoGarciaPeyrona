FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wakanda_shared /app/wakanda_shared

COPY services/gateway_api /app/services/gateway_api

ENV PYTHONPATH=/app
ENV PORT=8080

CMD ["uvicorn", "services.gateway_api.gateway_main:app", "--host", "0.0.0.0", "--port", "8080"]