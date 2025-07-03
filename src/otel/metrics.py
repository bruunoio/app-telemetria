from gc import callbacks
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
import random
from typing import Iterable
from opentelemetry.metrics import CallbackOptions, Observation
import psutil
import os

APP_NAME = os.getenv("APP_NAME", "app-a")

# Configuração do Prometheus como leitor de métricas
prometheus_reader = PrometheusMetricReader()
# setando o provider de metrics - MeterProvider
metrics.set_meter_provider(
    MeterProvider(
        metric_readers=[prometheus_reader]
    )
)
# Criando o meter - Meter
meter = metrics.get_meter(APP_NAME)

# MÉTRICAS CUSTOMIZADAS

# Metrica do tipo COUNTER

requests_counter = meter.create_counter(
    name="app_requests_total",
    description="Número de requisições processadas",
    unit="1", # unidade de medida
)
# Função para gerar um valor aleatório
def get_random_value(options: CallbackOptions) -> Iterable[Observation]:
    random_value = random.randint(1, 100)
    yield Observation(
        random_value, {"service": APP_NAME}
        )
# Forma assíncrona de incrementar a métrica counter - Randomicamente
random_counter = meter.create_observable_counter(
    name="app_random_value_total",
    description="Contador de valores aleatórios",
    callbacks=[get_random_value],
)
# Metrica do tipo GAUGE

active_requests_gauge = meter.create_gauge(
    name="app_active_requests",
    description="Número de requisições ativas",
    unit="1",
)
# GAUGE assíncrona
process = psutil.Process()

# Função para obter o uso de memória do processo
def get_memory_usage(options: CallbackOptions) -> Iterable[Observation]:
    memory_usage = process.memory_percent()
    yield Observation(
        memory_usage, {"service": APP_NAME}
    )
# Forma assíncrona de incrementar a métrica Gauge - Randomicamente
memory_gauge = meter.create_observable_gauge(
    name="app_memory_usage",
    description="Uso de memória do processo",
    callbacks=[get_memory_usage],
)
# Metrica do tipo HISTOGRAM

response_time_histogram = meter.create_histogram(
    name="app_response_time_seconds",
    description="Tempo de resposta das requisições em segundos",
    unit="s",
    explicit_bucket_boundaries_advisory=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5] # range de buckets para o histogram
)