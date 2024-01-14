from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import prometheus_client

from modules.helpers import get_expected_arrivals, map_expected_arrival_to_stop
from modules.metrics import MetricsHandler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MetricsHandler.instance()


@app.get("/predictions")
def predictions():
    try:
        MetricsHandler.request_count.inc()
        MetricsHandler.cache_last_updated.set_to_current_time()
        expected_arrivals = get_expected_arrivals()
        stops = list(map(map_expected_arrival_to_stop, expected_arrivals))
        return stops
    except Exception as e:
        error, status_code, status, response = e.args
        details = str(
            {
                "status": str(status),
                "error": str(error),
                "response": str(response),
            }
        )
        raise HTTPException(status_code, details)


@app.get("/metrics")
def get_metrics():
    return Response(
        media_type="text/plain",
        content=prometheus_client.generate_latest(),
    )
