import os
import json
import requests
from dotenv import load_dotenv
from endpoint_cache import check_cache, use_cache

load_dotenv()


@check_cache(use_cache())
def get_operators():
    response = json.loads(
        requests.get(
            "http://api.511.org/transit/operators?api_key=" + os.getenv("511_API_TOKEN")
        ).content
    )
    return response


@check_cache(use_cache())
def get_lines(operator_id: str = "SC"):
    response = json.loads(
        requests.get(
            "http://api.511.org/transit/lines?api_key="
            + os.getenv("511_API_TOKEN")
            + "&operator_id="
            + operator_id
        ).content
    )
    return response


@check_cache(use_cache())
def get_stops(operator_id: str = "SC", line_id: str = "Rapid 500"):
    response = json.loads(
        requests.get(
            "http://api.511.org/transit/stops?api_key="
            + os.getenv("511_API_TOKEN")
            + "&operator_id="
            + operator_id
            + "&line_id="
            + line_id
        ).content
    )
    return response


@check_cache(use_cache())
def get_expected_arrivals(operator_id: str = "SC", stop_id: str = "64995"):
    response = json.loads(
        requests.get(
            "http://api.511.org/transit/StopMonitoring?api_key="
            + os.getenv("511_API_TOKEN")
            + "&agency="
            + operator_id
            + "&stopcode="
            + stop_id
        ).content
    )
    return response
