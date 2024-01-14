from collections import defaultdict
from datetime import datetime
import requests
import json
import yaml

from modules.metrics import MetricsHandler
from modules.types import Predictions, Stop

MetricsHandler.instance()

EXTERNAL_API_ERROR_STATUS = {
    401: "Unauthorized",
    404: "Not Found",
    500: "Internal Server Error",
}


def get_expected_arrivals():
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)
    print(config)
    return list(
        map(
            lambda stop: get_expected_arrival(config["api_key"], stop),
            config["stops"],
        )
    )


def get_expected_arrival(api_key, stop):
    response = {
        **get_data(
            "http://api.511.org/transit/StopMonitoring?api_key="
            + str(api_key)
            + "&agency="
            + str(stop["operator"])
            + "&stopcode="
            + str(stop["stop_id"])
        ),
        **{"stop_id": stop["stop_id"], "operator": stop["operator"]},
    }
    if "error" in response:
        raise Exception(
            response["error"],
            response["status_code"],
            response["status"],
            response["response"],
        )
    return response


@MetricsHandler.external_api_latency.time()
def get_data(url: str):
    try:
        response = requests.get(url)
        if response.status_code in EXTERNAL_API_ERROR_STATUS:
            MetricsHandler.external_api_http_response_codes.labels(
                response.status_code
            ).inc()
            return {
                "error": "Error getting data from 511 API",
                "status_code": response.status_code,
                "status": EXTERNAL_API_ERROR_STATUS[response.status_code],
                "response": response.text,
            }
        MetricsHandler.external_api_http_response_codes.labels(200).inc()
        return json.loads(response.content)
    except requests.exceptions.RequestException as error:
        return {
            "error": "Error getting data from 511 API",
            "status_code": 520,
            "status": "Unknown Error",
            "response": error,
        }


def map_expected_arrival_to_stop(expected_arrival) -> Stop:
    monitored_vehicle_journeys = [
        monitored_stop_visit["MonitoredVehicleJourney"]
        for monitored_stop_visit in expected_arrival["ServiceDelivery"][
            "StopMonitoringDelivery"
        ]["MonitoredStopVisit"]
    ]
    if not monitored_vehicle_journeys:
        raise Exception(
            "No expected arrivals found.",
            404,
            "Not Found",
            {
                "ServiceDelivery": expected_arrival["ServiceDelivery"],
            },
        )
    stop_id = expected_arrival["stop_id"]
    operator = expected_arrival["operator"]
    stop_name = monitored_vehicle_journeys[0]["MonitoredCall"]["StopPointName"]
    route_times = map_route_times(monitored_vehicle_journeys)
    predictions: list[Predictions] = [
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
