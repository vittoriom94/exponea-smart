import logging
import os

from opentelemetry import trace
from opentelemetry.exporter.zipkin.proto.http import ZipkinExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

MAX_FIRST_TIMEOUT_MS = 300
TIMEOUT_TOLERANCE = 0.2
RETRIES = 2

EXPONEA_ENDPOINT = "https://exponea-engineering-assignment.appspot.com/api/work"

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
ZIPKIN_ENDPOINT = os.environ.get("ZIPKIN_ENDPOINT", "http://localhost:9411")


resource = Resource(attributes={
    SERVICE_NAME: "exponea"
})

zipkin_exporter = ZipkinExporter(endpoint=f"{ZIPKIN_ENDPOINT}/api/v2/spans")

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(zipkin_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


def configure_logger():
    logging.basicConfig(level=LOG_LEVEL, format="%(levelname)-9s %(asctime)s - %(name)s - %(message)s")

