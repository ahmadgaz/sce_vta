import uvicorn
from fastapi import FastAPI
from datetime import datetime
from typing import TypedDict, List
from endpoint_cache import check_cache, use_cache
from external_api import get_expected_arrivals

app = FastAPI()


class Predictions(TypedDict):
    route: str
    times: List[str]


class Stop(TypedDict):
    id: str
    name: str
    predictions: List[Predictions]


@app.get("/predictions")
@check_cache(use_cache())
def predictions(
    operator_id: str = "SC", line_id: str = "Rapid 500", stop_id: str = "64995"
):
    try:
        stop_monitoring = get_expected_arrivals(operator_id, stop_id)
        if "Error" in stop_monitoring:
            raise Exception(stop_monitoring["Error"])
        monitored_stop_visits = [
            visit["MonitoredVehicleJourney"]
            for visit in stop_monitoring["ServiceDelivery"]["StopMonitoringDelivery"][
                "MonitoredStopVisit"
            ]
            if visit["MonitoredVehicleJourney"]["LineRef"] == line_id
        ]
        if not monitored_stop_visits:
            raise Exception("No monitored stop visits")
        stop_name = monitored_stop_visits[0]["MonitoredCall"]["StopPointName"]
        response: List[Stop] = [
            {
                "id": stop_id,
                "name": stop_name,
                "predictions": [
                    {
                        "route": line_id,
                        "times": [
                            datetime.fromisoformat(
                                visit["MonitoredCall"]["ExpectedArrivalTime"].rstrip(
                                    "Z"
                                )
                            )
                            for visit in monitored_stop_visits
                        ],
                    }
                ],
            }
        ]
        return response
    except Exception as error:
        return {"Error": error}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, access_log=True)
