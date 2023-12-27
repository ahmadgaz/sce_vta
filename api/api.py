import os
import json
import random
import requests
from fastapi import FastAPI
from dotenv import load_dotenv
from cache import check_cache, use_cache

load_dotenv()
app = FastAPI()


@app.get("/get_operators")
@check_cache(cache=use_cache())
def get_operators():
    response = json.loads(
        requests.get(
            "http://api.511.org/transit/operators?api_key=" + os.getenv("511_API_TOKEN")
        ).content
    )
    return response


@app.get("/get_lines")
@check_cache(cache=use_cache())
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


@app.get("/get_stops")
@check_cache(cache=use_cache())
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


@app.get("/get_patterns")
@check_cache(cache=use_cache())
def get_patterns(operator_id: str = "SC", line_id: str = "Rapid 500"):
    response = json.loads(
        requests.get(
            "http://api.511.org/transit/patterns?api_key"
            + os.getenv("511_API_TOKEN")
            + "&operator_id="
            + operator_id
            + "&line_id="
            + line_id
        ).content
    )
    return response
