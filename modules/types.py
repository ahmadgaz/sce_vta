from typing import TypedDict, TypeVar, List, Union

T = TypeVar("T")


class Predictions(TypedDict):
    route: str
    times: List[str]


class Stop(TypedDict):
    stop_id: str
    operator: str
    name: str
    predictions: List[Predictions]
