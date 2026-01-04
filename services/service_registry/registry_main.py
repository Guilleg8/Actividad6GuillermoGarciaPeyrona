from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import uvicorn
import logging

try:
    from wakanda_shared.telemetry import setup_telemetry
except ImportError:
    def setup_telemetry(app, name): pass

class ServiceRegistration(BaseModel):
    service_name: str
    url: str
    health_url: str

services_db: Dict[str, str] = {}

app = FastAPI(title="Wakanda Service Registry")

setup_telemetry(app, "service_registry")

@app.post("/register")
async def register_service(service: ServiceRegistration):

    services_db[service.service_name] = service.url
    logging.info(f"✅ Servicio Registrado: {service.service_name} en {service.url}")
    return {"status": "registered", "service": service.service_name}

@app.get("/discover/{service_name}")
async def discover_service(service_name: str):

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