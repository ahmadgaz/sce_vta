import uvicorn
from fastapi import FastAPI
from datetime import datetime
from collections import defaultdict
from external_api import get_expected_arrivals
from typing import TypedDict, TypeVar, List

app = FastAPI()

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
        expected_arrivals = get_expected_arrivals()
        if "Error" in expected_arrivals:
            raise Exception(expected_arrivals)
        stops = list(map(map_expected_arrival_to_stop, expected_arrivals))
        return stops
    except Exception as error:
        return error


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
    time = datetime.fromisoformat(
        mvj["MonitoredCall"]["ExpectedArrivalTime"].rstrip("Z")
    )
    route_times = map_route_times(monitored_vehicle_journeys, idx + 1)
    return {**route_times, route: [*route_times.get(route, []), time]}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, access_log=True)
