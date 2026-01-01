FROM python:3.9-slim

WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la librería común
COPY wakanda_shared /app/wakanda_shared

# --- DIFERENCIA AQUÍ ---
# Copiamos la carpeta del GATEWAY
COPY services/gateway_api /app/services/gateway_api

ENV PYTHONPATH=/app
ENV PORT=8080

# --- DIFERENCIA AQUÍ ---
# Ejecutamos gateway_main en el puerto 8080
CMD ["uvicorn", "services.gateway_api.gateway_main:app", "--host", "0.0.0.0", "--port", "8080"]