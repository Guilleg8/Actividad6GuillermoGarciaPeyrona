# Usamos una versión ligera de Python
FROM python:3.9-slim

# Creamos una carpeta de trabajo dentro del contenedor
WORKDIR /app

# 1. Copiamos el archivo de dependencias que está en la raíz del proyecto
#    (Docker lo encuentra porque el contexto de construcción es la raíz)
COPY requirements.txt .

# 2. Instalamos las librerías (FastAPI, Uvicorn, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiamos la carpeta compartida 'wakanda_shared' dentro del contenedor
COPY wakanda_shared /app/wakanda_shared

# 4. Copiamos SOLO la carpeta de este servicio específico
COPY services/service_registry /app/services/service_registry

# 5. Configuramos Python para que sepa buscar módulos en /app
ENV PYTHONPATH=/app

# 6. Comando de arranque (Fíjate que apunta a registry_main)
CMD ["uvicorn", "services.service_registry.registry_main:app", "--host", "0.0.0.0", "--port", "8000"]