import asyncio
import logging
import random
import httpx
import os
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from contextlib import asynccontextmanager

try:
    from wakanda_shared.telemetry import setup_telemetry
except ImportError:
    def setup_telemetry(app, name):
        pass

SERVICE_NAME = "gestion_trafico"
SERVICE_PORT = int(os.getenv("PORT", 8001))
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://service_registry:8000/register")


class TrafficAdjustment(BaseModel):
    new_green_seconds: int


class TrafficStatus(BaseModel):
    intersection_id: str
    timestamp: str
    vehicle_count: int
    average_speed_kmh: float
    signal_phase: str
    recommended_adjustment: TrafficAdjustment

class TrafficUpdate(BaseModel):
    intersection_id: str   # <--- ¡ESTE ES EL NOMBRE QUE BUSCAMOS!
    duration: int          # <--- ¡Y ESTE!

current_status = TrafficStatus(
    intersection_id="I-12",
    timestamp=datetime.utcnow().isoformat(),
    vehicle_count=0,
    average_speed_kmh=0.0,
    signal_phase="RED",
    recommended_adjustment=TrafficAdjustment(new_green_seconds=30)
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)

SIMULATION_RUNNING = False
CURRENT_GREEN_DURATION = 30  # Duración por defecto


async def simulate_traffic_cycle():

    global current_status
    phases = ["RED", "GREEN", "YELLOW"]

    while SIMULATION_RUNNING:
        vehicle_count = random.randint(0, 50)

        speed = max(5.0, 60.0 - vehicle_count * 0.8) if vehicle_count > 0 else 0.0

        current_phase = random.choice(phases)

        current_status = TrafficStatus(
            intersection_id="I-12",
            timestamp=datetime.utcnow().isoformat(),
            vehicle_count=vehicle_count,
            average_speed_kmh=round(speed, 2),
            signal_phase=current_phase,
            recommended_adjustment=TrafficAdjustment(new_green_seconds=CURRENT_GREEN_DURATION)
        )

        logger.debug(f"Simulación actualizada: {vehicle_count} vehículos, Fase {current_phase}")
        await asyncio.sleep(3)


async def register_service():
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "name": SERVICE_NAME,
                "url": f"http://gestion_trafico:{SERVICE_PORT}",  # Hostname de Docker
                "health_endpoint": f"http://gestion_trafico:{SERVICE_PORT}/health"
            }
            response = await client.post(REGISTRY_URL, json=payload, timeout=5.0)
            if response.status_code in [200, 201]:
                logger.info(f"✅ Servicio registrado exitosamente en {REGISTRY_URL}")
            else:
                logger.warning(f"⚠️ Fallo al registrar servicio: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ No se pudo contactar con el registry: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_telemetry(app, SERVICE_NAME)

    global SIMULATION_RUNNING
    SIMULATION_RUNNING = True
    simulation_task = asyncio.create_task(simulate_traffic_cycle())

    asyncio.create_task(register_service())

    yield

    SIMULATION_RUNNING = False
    simulation_task.cancel()
    logger.info("🛑 Servicio detenido")


app = FastAPI(
    title="Servicio de Gestión de Tráfico",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/status", response_model=TrafficStatus)
async def get_traffic_status():
    return current_status


@app.post("/adjust_signal")
async def adjust_traffic_signal(update: TrafficUpdate):
    global CURRENT_GREEN_DURATION

    logger.info(f"📡 Recibida solicitud de ajuste para intersección {update.intersection_id}")
    logger.info(f"⏱️ Ajustando duración de luz verde a {update.duration} segundos")

    CURRENT_GREEN_DURATION = update.duration

    return {
        "status": "success",
        "message": f"Duración actualizada a {update.duration}s para intersección {update.intersection_id}"
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)