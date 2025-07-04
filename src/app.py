import os
import time
import random
import requests
from fastapi import FastAPI, Response, status, Request
from typing import List
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from otel.metrics import requests_counter, active_requests_gauge, response_time_histogram

# ================================
#  CONFIGURAÇÃO DA APLICAÇÃO
# ================================

APP_NAME = os.getenv("APP_NAME", "app-a")
APP_URL_DESTINO = os.getenv("APP_URL_DESTINO", "")

# Simulação de problemas
APP_ERRORS = int(os.getenv("APP_ERRORS", "0"))  # Porcentagem de erro (0 a 100)
APP_LATENCY = int(os.getenv("APP_LATENCY", "0"))  # Tempo máximo de atraso (em ms)

app = FastAPI()

@app.get("/")
def read_root():
    active_requests_gauge.set(1, {"app": APP_NAME, "endpoint": "/"}) # Incrementando a métrica de requisições ativas
    requests_counter.add(1, {"app": APP_NAME, "endpoint": "/"}) # Incrementando a métrica de requisições
    start_time = time.time() # Marca o tempo atual do processamento
    elapsed_time = time.time() - start_time
    response_time_histogram.record(elapsed_time, {"app": APP_NAME, "endpoint": "/"})  # Incrementando o valor do Histogram com record
    return {"message": f"Esse é o serviço {APP_NAME}"}
# Definindo o exporte de metrics
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/process")
def process_request(payload: List[str], response: Response, request: Request):
    """
    Endpoint que processa um payload, simula falhas e latência variável,
    e propaga a requisição para outros serviços.
    """
    
    start_time = time.time()  # Marca o tempo atual do processamento - Histogram

    active_requests_gauge.set(10, {"app": APP_NAME, "endpoint": "/process"})
    
    requests_counter.add(1, {"app": APP_NAME, "endpoint": "/process"}) # Incrementando a métrica de requisições

    original_payload = payload.copy()
    original_payload.append(APP_NAME)

    # Simulação de latência variável
    if APP_LATENCY > 0:
        simulated_latency = random.randint(0, APP_LATENCY)  # Define um atraso aleatório entre 0 e APP_LATENCY
        time.sleep(simulated_latency / 1000)  # Converte ms para segundos

    # Simulação de erro com base na porcentagem definida
    if random.randint(1, 100) <= APP_ERRORS:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_msg = f"Erro simulado em {APP_NAME}"
        return {"error": error_msg}

    # Se houver serviços de destino, propaga a requisição
    if APP_URL_DESTINO:
        urls = APP_URL_DESTINO.split(',')
        for url in urls:
            try:
                resp = requests.post(
                    f"{url}/process",
                    json=original_payload,
                    timeout=5
                )

                if resp.status_code == 200:
                    original_payload = resp.json()
                else:
                    response.status_code = status.HTTP_502_BAD_GATEWAY
                    return {"error": f"Erro ao enviar para {url}: {resp.status_code}"}

            except requests.RequestException as e:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"error": f"Falha na requisição para {url}: {str(e)}"}

    elapsed_time = time.time() - start_time  # Calcula o tempo total de processamento
    response_time_histogram.record(elapsed_time, {"app": APP_NAME, "endpoint": "/process"})  # Incrementando valor Histogram com record

    return original_payload