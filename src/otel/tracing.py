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

APP_NAME = os.getenv("APP_NAME", "app-a") # Nome da aplicação

resource = Resource.create({"SERVICE_NAME": APP_NAME, "SERVICE_VERSION": "1.0.0"}) # Criando o recurso com o nome e versão do serviço`

provider = TracerProvider(resource=resource) # Criando o provider de trace com o recurso

processor = BatchSpanProcessor(ConsoleSpanExporter()) # Criando o processador de spans com o exportador de console

provider.add_span_processor(processor) # Adicionando o processador ao provider

trace.set_tracer_provider(provider) # Definindo o provider de trace

tracer = trace.get_tracer(APP_NAME) # Obtendo o tracer para a aplicação