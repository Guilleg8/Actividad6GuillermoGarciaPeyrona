FROM python:3.9-slim

WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la librería común
COPY wakanda_shared /app/wakanda_shared

# --- DIFERENCIA AQUÍ ---
# Copiamos la carpeta de TRAFICO
COPY services/gestion_trafico /app/services/gestion_trafico

ENV PYTHONPATH=/app
# Variable de entorno para saber en qué puerto escuchar internamente
ENV PORT=8001

# --- DIFERENCIA AQUÍ ---
# Ejecutamos traffic_main en el puerto 8001
CMD ["uvicorn", "services.gestion_trafico.traffic_main:app", "--host", "0.0.0.0", "--port", "8001"]