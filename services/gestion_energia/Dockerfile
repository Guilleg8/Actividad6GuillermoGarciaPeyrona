FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wakanda_shared /app/wakanda_shared
COPY services/gestion_energia /app/services/gestion_energia
ENV PYTHONPATH=/app
ENV PORT=8002
CMD ["uvicorn", "services.gestion_energia.energy_main:app", "--host", "0.0.0.0", "--port", "8002"]