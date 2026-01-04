from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI


def setup_telemetry(app: FastAPI, service_name: str, jaeger_host: str = "jaeger", jaeger_port: int = 4317):

    provider = TracerProvider()

    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=f"http://{jaeger_host}:{jaeger_port}"))
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)

    Instrumentator().instrument(app).expose(app)

    print(f"🔭 Telemetría configurada para: {service_name}")