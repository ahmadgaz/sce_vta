from re import M
import yaml
import json
import requests

from api.metrics import MetricsHandler

MetricsHandler.instance()

EXTERNAL_API_ERROR_STATUS = {
    401: "Unauthorized",
    404: "Not Found",
    500: "Internal Server Error",
}


def get_expected_arrivals():
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)
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
