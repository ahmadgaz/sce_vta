import yaml
import json
import requests


def get_expected_arrivals():
    try:
        with open("config.yml", "r") as file:
            config = yaml.safe_load(file)
        return list(
            map(
                lambda stop: get_expected_arrival(config["api_key"], stop),
                config["stops"],
            )
        )
    except Exception as error:
        return error


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
    if "Error" in response:
        raise response
    return response


def get_data(url: str):
    return json.loads(requests.get(url).content)
