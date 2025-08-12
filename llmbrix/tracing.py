import socket
from contextlib import contextmanager
from typing import Callable

from opentelemetry import trace
from opentelemetry.trace import Tracer

_tracer: Tracer = trace.get_tracer(__name__)
_is_configured = False


def _is_collector_reachable(host: str, port: int, timeout: float = 0.25) -> bool:
    """Return True iff a TCP connection to host:port succeeds within timeout."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def configure_arize_tracing(
    project_name: str,
    phoenix_collector_endpoint: str = "http://localhost:4317",
):
    """
    Configures Phoenix + OpenInference tracing IFF everything is available & reachable.
    Otherwise, stays completely silent and leaves a no-op tracer in place.
    """
    global _tracer, _is_configured

    # Import deps lazily so a missing package silently disables tracing
    try:
        from urllib.parse import urlparse

        from openinference.instrumentation.openai import OpenAIInstrumentor
        from phoenix.otel import register
    except Exception:
        # Any import problem => no tracing
        _tracer = _NoopTracer()
        _is_configured = False
        return

    # Parse endpoint and preflight reachability before we register anything
    try:
        parsed = urlparse(phoenix_collector_endpoint)
        host = parsed.hostname or "localhost"
        port = parsed.port or 4317
    except Exception:
        # Malformed endpoint => no tracing
        _tracer = _NoopTracer()
        _is_configured = False
        return

    if not _is_collector_reachable(host, port):
        # Collector not up => no tracing (prevents exporter retry spam)
        _tracer = _NoopTracer()
        _is_configured = False
        return

    # If we’re here, deps exist and collector is reachable; set up tracing.
    try:
        tracer_provider = register(
            project_name=project_name,
            endpoint=phoenix_collector_endpoint,
            batch=True,  # keep Phoenix defaults
        )
        OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
        _tracer = trace.get_tracer(__name__, tracer_provider=tracer_provider)
        _is_configured = True
    except Exception:
        # Any runtime failure => fall back to no-op, keep quiet
        _tracer = _NoopTracer()
        _is_configured = False


def get_tracer() -> Tracer:
    """
    Returns a tracer that always works.
    If Phoenix is not configured, returns tracer with no-op decorators.
    """
    if _is_configured:
        return _tracer
    return _NoopTracer()


class _NoopTracer:
    """A no-op tracer with decorators that do nothing, and a context manager span."""

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
