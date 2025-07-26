from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor


def configure_arize_tracing(
        project_name: str,
        phoenix_collector_endpoint: str = "http://localhost:4317"
):
    """
    Configures Phoenix + OpenInference tracing.
    Must be called before importing any of instrumented libraries and modules (e.g. GptOpenAI, Agent, etc.)

    :param project_name: Name of application for tracing context.
    :param phoenix_collector_endpoint: URL Phoenix collector endpoint is running
    """
    OpenAIInstrumentor().instrument( tracer_provider=register(project_name=project_name, endpoint=phoenix_collector_endpoint))
