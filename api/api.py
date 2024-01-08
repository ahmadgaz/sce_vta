from tracemalloc import stop
import prometheus_client
from datetime import datetime
from collections import defaultdict
from fastapi import FastAPI, Response
from typing import TypedDict, TypeVar, List
from external_api import get_expected_arrivals
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

requests_count = prometheus_client.Counter(
    "requests_count",
    "Total number of requests",
)

T = TypeVar("T")


class Predictions(TypedDict):
    route: str
    times: List[str]


class Stop(TypedDict):
    stop_id: str
    operator: str
    name: str
    predictions: List[Predictions]


@app.get("/predictions")
def predictions():
    try:
        requests_count.inc()
        expected_arrivals = get_expected_arrivals()
        if "Error" in expected_arrivals:
            raise Exception(expected_arrivals)
        stops = list(map(map_expected_arrival_to_stop, expected_arrivals))
        return stops
    except Exception as error:
        return error


@app.get("/metrics")
def get_metrics():
    return Response(
        media_type="text/plain",
        content=prometheus_client.generate_latest(),
    )


def map_expected_arrival_to_stop(expected_arrival) -> Stop:
    monitored_vehicle_journeys = [
        monitored_stop_visit["MonitoredVehicleJourney"]
        for monitored_stop_visit in expected_arrival["ServiceDelivery"][
            "StopMonitoringDelivery"
        ]["MonitoredStopVisit"]
    ]
    if not monitored_vehicle_journeys:
        raise Exception(
            {
                "Error": "No expected arrivals found.",
                "ServiceDelivery": expected_arrival["ServiceDelivery"],
            }
        )
    stop_id = expected_arrival["stop_id"]
    operator = expected_arrival["operator"]
    stop_name = monitored_vehicle_journeys[0]["MonitoredCall"]["StopPointName"]
    route_times = map_route_times(monitored_vehicle_journeys)
    predictions: List[Predictions] = [
        {"route": route, "times": times} for route, times in route_times.items()
    ]
    return {
        "stop_id": stop_id,
        "operator": operator,
        "name": stop_name,
        "predictions": predictions,
    }


def map_route_times(monitored_vehicle_journeys, idx=0):
    if idx >= len(monitored_vehicle_journeys):
        return defaultdict(list)
    mvj = monitored_vehicle_journeys[idx]
    route = mvj["LineRef"]
    if not route:
        return map_route_times(monitored_vehicle_journeys, idx + 1)
    if mvj["MonitoredCall"]["ExpectedArrivalTime"]:
        time = datetime.fromisoformat(
            mvj["MonitoredCall"]["ExpectedArrivalTime"].rstrip("Z")
        )
    elif mvj["MonitoredCall"]["AimedArrivalTime"]:
        time = datetime.fromisoformat(
            mvj["MonitoredCall"]["AimedArrivalTime"].rstrip("Z")
        )
    else:
        return map_route_times(monitored_vehicle_journeys, idx + 1)
    route_times = map_route_times(monitored_vehicle_journeys, idx + 1)
    return {**route_times, route: [*route_times.get(route, []), time]}
