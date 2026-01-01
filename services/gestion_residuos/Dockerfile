FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wakanda_shared /app/wakanda_shared
COPY services/gestion_residuos /app/services/gestion_residuos
ENV PYTHONPATH=/app
ENV PORT=8004
CMD ["uvicorn", "services.gestion_residuos.waste_main:app", "--host", "0.0.0.0", "--port", "8004"]