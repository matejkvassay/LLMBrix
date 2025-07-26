from contextlib import contextmanager
from typing import Callable

from opentelemetry import trace
from opentelemetry.trace import Tracer
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

_tracer: Tracer = trace.get_tracer(__name__)
_is_configured = False


def configure_arize_tracing(
        project_name: str,
        phoenix_collector_endpoint: str = "http://localhost:4317",
):
    """
    Configures Phoenix + OpenInference tracing.
    Must be called before importing any of instrumented libraries and modules (e.g. GptOpenAI, Agent, etc.)
    """
    global _tracer, _is_configured

    try:
        from phoenix.otel import register
        from openinference.instrumentation.openai import OpenAIInstrumentor

        exporter = OTLPSpanExporter(
            endpoint=phoenix_collector_endpoint,
            insecure=True,  # or set up TLS config if using https
            timeout=1,  # fail fast
            # Disable retries by setting no retry policy
            # OpenTelemetry Python doesn't expose retry config directly,
            # but setting timeout + fast-fail + no custom retry policy is best you can do for now.
        )


        tracer_provider = register(
            project_name=project_name,
            endpoint=phoenix_collector_endpoint,
            batch=True
        )
        OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
        _tracer = trace.get_tracer(__name__, tracer_provider=tracer_provider)
        _is_configured = True

    except ImportError:
        print("[tracing] Phoenix or OpenInference not available, using noop tracer.")


def get_tracer() -> Tracer:
    """
    Returns a tracer that always works.
    If Phoenix is not configured, returns tracer with no-op `.chain()` decorator.
    """
    if _is_configured:
        return _tracer

    return _NoopTracer()


class _NoopTracer:
    """A no-op tracer with a `chain()` decorator that does nothing."""

    def start_as_current_span(self, name):
        return _noop_span(name)

    def chain(self, name: str = None, description: str = None) -> Callable:
        def decorator(func):
            return func

        return decorator

    def agent(self, name: str = None, description: str = None) -> Callable:
        def decorator(func):
            return func

        return decorator

    def tool(self, name: str = None, description: str = None) -> Callable:
        def decorator(func):
            return func

        return decorator

    def llm(self, name: str = None, description: str = None) -> Callable:
        def decorator(func):
            return func

        return decorator


@contextmanager
def _noop_span(name: str):
    yield