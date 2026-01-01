FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wakanda_shared /app/wakanda_shared
COPY services/gestion_agua /app/services/gestion_agua
ENV PYTHONPATH=/app
ENV PORT=8003
CMD ["uvicorn", "services.gestion_agua.water_main:app", "--host", "0.0.0.0", "--port", "8003"]