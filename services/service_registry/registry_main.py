# services/service_registry/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import uvicorn
import logging

# Importamos nuestra librería compartida (asumiendo que ejecutamos desde root o docker gestiona el path)
# En local, asegúrate de tener wakanda_shared en el PYTHONPATH o copia la carpeta.
# Para este paso, asumiremos que Docker se encarga del path, pero te dejo un try/except para pruebas locales.
try:
    from wakanda_shared.telemetry import setup_telemetry
except ImportError:
    # Mock para prueba local sin la carpeta compartida
    def setup_telemetry(app, name): pass

# --- Modelos de Datos ---
class ServiceRegistration(BaseModel):
    service_name: str  # Ej: "gestion_trafico"
    url: str           # Ej: "http://traffic_service:8001"
    health_url: str    # Ej: "http://traffic_service:8001/health"

# --- Estado en Memoria ---
# Diccionario: { "gestion_trafico": "http://traffic_service:8001", ... }
services_db: Dict[str, str] = {}

app = FastAPI(title="Wakanda Service Registry")

# Configurar telemetría
setup_telemetry(app, "service_registry")

@app.post("/register")
async def register_service(service: ServiceRegistration):
    """
    Los microservicios llaman aquí al arrancar para decir 'Estoy vivo'.
    """
    services_db[service.service_name] = service.url
    logging.info(f"✅ Servicio Registrado: {service.service_name} en {service.url}")
    return {"status": "registered", "service": service.service_name}

@app.get("/discover/{service_name}")
async def discover_service(service_name: str):
    """
    El Gateway llama aquí para preguntar '¿Dónde está X servicio?'.
    """
    url = services_db.get(service_name)
    if not url:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"url": url}

@app.get("/health")
async def health_check():
    return {"status": "ok", "registered_services_count": len(services_db)}

@app.get("/services")
async def list_services():
    return services_db

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)