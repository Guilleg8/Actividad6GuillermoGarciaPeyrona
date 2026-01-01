import asyncio
import logging
import httpx
import os
import random
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager

try:
    from wakanda_shared.telemetry import setup_telemetry
except ImportError:
    def setup_telemetry(app, name): pass

SERVICE_NAME = "gestion_agua"
SERVICE_PORT = int(os.getenv("PORT", 8003))
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://service_registry:8000/register")

class LeakAlert(BaseModel):
    zone_id: str
    severity: str

active_leaks = []

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

app = FastAPI(lifespan=lifespan, title="Wakanda Water")
setup_telemetry(app, SERVICE_NAME)

@app.get("/water/pressure")
async def get_pressure():
    # Simula presión variable
    return {
        "sector_1_psi": random.randint(40, 60),
        "sector_2_psi": random.randint(35, 55),
        "status": "NORMAL"
    }

@app.post("/water/leak_alert")
async def report_leak(alert: LeakAlert):
    active_leaks.append(alert)
    logging.warning(f"💧 FUGA DETECTADA en {alert.zone_id}")
    return {"status": "alert_registered", "active_leaks_count": len(active_leaks)}

@app.get("/health")
async def health(): return {"status": "ok"}