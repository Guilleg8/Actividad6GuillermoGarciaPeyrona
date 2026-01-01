import asyncio
import logging
import httpx
import os
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import List

try:
    from wakanda_shared.telemetry import setup_telemetry
except ImportError:
    def setup_telemetry(app, name): pass

SERVICE_NAME = "seguridad_vigilancia"
SERVICE_PORT = int(os.getenv("PORT", 8005))
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://service_registry:8000/register")

class SecurityAlert(BaseModel):
    location: str
    anomaly_type: str
    description: str

event_log: List[SecurityAlert] = []

async def register_service():
    await asyncio.sleep(3)
    async with httpx.AsyncClient() as client:
        try:
            my_url = f"http://{SERVICE_NAME}:{SERVICE_PORT}"
            await client.post(REGISTRY_URL, json={
                "service_name": SERVICE_NAME, "url": my_url, "health_url": f"{my_url}/health"
            })
            logging.info(f"✅ {SERVICE_NAME} Registrado")
        except Exception:
            logging.error(f"⚠️ Fallo registro {SERVICE_NAME}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(register_service())
    yield

app = FastAPI(lifespan=lifespan, title="Wakanda Security")
setup_telemetry(app, SERVICE_NAME)

@app.post("/security/alert")
async def create_alert(alert: SecurityAlert):
    logging.critical(f"🚨 ALERTA DE SEGURIDAD: {alert.anomaly_type} en {alert.location}")
    event_log.append(alert)
    return {"status": "alert_broadcasted"}

@app.get("/security/events")
async def get_events():
    return event_log

@app.get("/health")
async def health(): return {"status": "ok"}