# wakanda_shared/telemetry.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI


def setup_telemetry(app: FastAPI, service_name: str, jaeger_host: str = "jaeger", jaeger_port: int = 4317):
    """
    Configura OpenTelemetry (Trazas) y Prometheus (Métricas) para cualquier servicio.
    """

    # 1. Configuración de OpenTelemetry (Trazabilidad)
    # Define quién provee las trazas
    provider = TracerProvider()

    # Configura el exportador para enviar datos a Jaeger (vía OTLP gRPC)
    # Si falla la conexión, no rompe la app (gracias a BatchSpanProcessor)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=f"http://{jaeger_host}:{jaeger_port}"))
    provider.add_span_processor(processor)

    # Establece el proveedor global
    trace.set_tracer_provider(provider)

    # Instrumenta automáticamente FastAPI (captura peticiones HTTP)
    FastAPIInstrumentor.instrument_app(app)

    # 2. Configuración de Prometheus (Métricas)
    # Expone automáticamente el endpoint /metrics
    Instrumentator().instrument(app).expose(app)

    print(f"🔭 Telemetría configurada para: {service_name}")