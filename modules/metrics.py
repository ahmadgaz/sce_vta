from typing import Any, Callable, Union
import prometheus_client


class _MetricLambdaWrapper:
    def __init__(self, metric_lambda: Callable):
        if not callable(metric_lambda):
            raise ValueError("metric_lambda must be callable")
        self.metric_lambda = metric_lambda


class MetricsHandler:
    _instance = None

    external_api_latency: Union[
        Any, prometheus_client.Histogram
    ] = _MetricLambdaWrapper(
        lambda: prometheus_client.Histogram(
            "EXTERNAL_API_LATENCY",
            "Latency of 511 API requests",
        )
    )
    external_api_http_response_codes: Union[
        Any, prometheus_client.Counter
    ] = _MetricLambdaWrapper(
        lambda: prometheus_client.Counter(
            "EXTERNAL_API_HTTP_RESPONSE_CODES",
            "HTTP response codes of 511 API requests",
            ["code"],
        )
    )
    request_count: Union[Any, prometheus_client.Counter] = _MetricLambdaWrapper(
        lambda: (prometheus_client.Counter("REQUEST_COUNT", "Total number of requests"))
    )
    cache_last_updated: Union[Any, prometheus_client.Gauge] = _MetricLambdaWrapper(
        lambda: (
            prometheus_client.Gauge("CACHE_LAST_UPDATED", "Last time cache was updated")
        )
    )

    def __init__(self):
        raise RuntimeError("Call MetricsHandler.instance() instead")

    def init(self) -> None:
        initial_attributes = list(vars(self).items())
        for attr_name, attr_value in initial_attributes:
            if isinstance(attr_value, _MetricLambdaWrapper):
                if not attr_name.startswith("_set_"):
                    setattr(self, f"_set_{attr_name}", attr_value)
                setattr(
                    self, attr_name.replace("_set_", "", 1), attr_value.metric_lambda()
                )

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls.init(cls)
        return cls._instance
