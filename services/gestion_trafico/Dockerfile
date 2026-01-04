FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wakanda_shared /app/wakanda_shared


COPY services/gestion_trafico /app/services/gestion_trafico

ENV PYTHONPATH=/app
ENV PORT=8001

CMD ["uvicorn", "services.gestion_trafico.traffic_main:app", "--host", "0.0.0.0", "--port", "8001"]