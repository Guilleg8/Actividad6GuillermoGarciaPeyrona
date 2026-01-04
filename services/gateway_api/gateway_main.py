import httpx
import logging
import os
import aiobreaker
from fastapi import FastAPI, HTTPException, Request, Response
from datetime import timedelta

try:
    from wakanda_shared.telemetry import setup_telemetry
except ImportError:
    def setup_telemetry(app, name):
        pass

SERVICE_NAME = "gateway_api"
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://service_registry:8000")

app = FastAPI(title="Wakanda Gateway")
setup_telemetry(app, SERVICE_NAME)

circuit_breaker = aiobreaker.CircuitBreaker(
    fail_max=3,
    timeout_duration=timedelta(seconds=30)
)


async def get_service_url(service_name: str) -> str:
    """Consulta al Service Registry la URL de un microservicio."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{REGISTRY_URL}/discover/{service_name}")
            if resp.status_code == 200:
                return resp.json()["url"]
            else:
                return None
        except httpx.RequestError:
            logging.error("❌ No se puede contactar con el Service Registry")
            return None


@circuit_breaker
async def make_request(method: str, url: str, json_data=None):

    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, json=json_data)
        response.raise_for_status()
        return response



@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_proxy(service_name: str, path: str, request: Request):

    target_base_url = await get_service_url(service_name)

    if not target_base_url:
        raise HTTPException(status_code=503, detail=f"Service '{service_name}' not found in registry")

    target_url = f"{target_base_url}/{service_name}/{path}"
    target_url = f"{target_base_url}/{path}"

    body = await request.json() if request.method in ["POST", "PUT"] else None

    try:
        upstream_response = await make_request(request.method, target_url, body)
        return upstream_response.json()

    except aiobreaker.CircuitBreakerError:
        logging.warning(f"🔥 Circuit Breaker Abierto para {service_name}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable (Circuit Breaker Open)")

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Upstream service unreachable")


@app.get("/health")
async def health_check():
    return {"status": "ok"}