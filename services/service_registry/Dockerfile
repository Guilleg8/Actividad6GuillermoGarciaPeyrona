FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY wakanda_shared /app/wakanda_shared

COPY services/service_registry /app/services/service_registry

ENV PYTHONPATH=/app

CMD ["uvicorn", "services.service_registry.registry_main:app", "--host", "0.0.0.0", "--port", "8000"]