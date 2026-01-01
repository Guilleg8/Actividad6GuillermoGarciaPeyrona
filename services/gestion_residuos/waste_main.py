import asyncio
import logging
import httpx
import os
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager

try:
    from wakanda_shared.telemetry import setup_telemetry
except ImportError:
    def setup_telemetry(app, name): pass

SERVICE_NAME = "gestion_residuos"
SERVICE_PORT = int(os.getenv("PORT", 8004))
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://service_registry:8000/register")

class PickupRequest(BaseModel):
    container_id: str
    fill_level_percent: int

pickup_queue = []

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

app = FastAPI(lifespan=lifespan, title="Wakanda Waste")
setup_telemetry(app, SERVICE_NAME)

@app.get("/waste/containers")
async def get_containers():
    # Datos simulados
    return [
        {"id": "C-101", "location": "Plaza Central", "fill_percent": 85},
        {"id": "C-102", "location": "Av. Wakanda", "fill_percent": 20}
    ]

@app.post("/waste/request_pickup")
async def request_pickup(request: PickupRequest):
    if request.fill_level_percent > 70:
        pickup_queue.append(request.container_id)
        return {"status": "scheduled", "queue_position": len(pickup_queue)}
    return {"status": "ignored", "reason": "fill level too low"}

@app.get("/health")
async def health(): return {"status": "ok"}