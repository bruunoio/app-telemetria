from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
import os
from opentelemetry.semconv.attributes.service_attributes import(
    SERVICE_NAME, # Atributo de nome do serviço
    SERVICE_VERSION, # Atributo de versão do serviço
)
from opentelemetry.sdk.trace.export import ( # trabalhando com exportadores de spans
    BatchSpanProcessor, # Define o processamento em lote dos spans
    ConsoleSpanExporter, # Exporta para o console
)

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter # Exportador OTLP para spans

OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4318/v1/traces") # Endpoint do OTLP

APP_NAME = os.getenv("APP_NAME", "app-a") # Nome da aplicação

resource = Resource.create({"SERVICE_NAME": APP_NAME, "SERVICE_VERSION": "1.0.0"}) # Criando o recurso com o nome e versão do serviço`

provider = TracerProvider(resource=resource) # Criando o provider de trace com o recurso

processor = BatchSpanProcessor(ConsoleSpanExporter()) # Criando o processador de spans com o exportador de console

processor_cosole = BatchSpanProcessor(ConsoleSpanExporter()) # Criando o processador de spans com o exportador de console

processor_otlp = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_ENDPOINT)) # Criando o processador de spans com o exportador OTLP

# provider.add_span_processor(processor_cosole) # Adicionando o processador ao provider
provider.add_span_processor(processor_otlp) # Adicionando o processador OTLP ao provider

trace.set_tracer_provider(provider) # Definindo o provider de trace

tracer = trace.get_tracer(APP_NAME) # Obtendo o tracer para a aplicação