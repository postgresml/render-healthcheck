from typing import Optional
from fastapi import FastAPI
from pgml import Database

import os
from contextlib import contextmanager

# Track timings
from datetime import datetime
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_resource import MetricResource
from datadog_api_client.v2.model.metric_series import MetricSeries

local_pgml = "postgres:///pgml"

app = FastAPI()
configuration = Configuration(api_key=os.environ.get("DD_API_KEY"))


@contextmanager
def timing(name, *args, **kwargs):
    start = datetime.now()
    yield
    end = datetime.now()
    duration = float(int((end - start).total_seconds() * 1000.0))
    submit_metric(name, duration)


def submit_metric(name, value):
    body = MetricPayload(
        series=[
            MetricSeries(
                metric=name,
                type=MetricIntakeType.GAUGE,
                points=[
                    MetricPoint(
                        timestamp=int(datetime.now().timestamp()),
                        value=value,
                    ),
                ],
                resources=[
                    MetricResource(
                        name="postgresml-healthcheck.onrender.com",
                        type="host",
                    ),
                ],
            ),
        ],
    )
    print(body)

    with ApiClient(configuration) as api_client:
        api_instance = MetricsApi(api_client)
        response = api_instance.submit_metrics(body=body)


with timing("custom.vendor.render.connect"):
    database = Database(os.environ.get("PGML_DATABASE_URL", local_pgml))


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/healthcheck")
async def healthcheck():
    with timing("custom.vendor.render.healthcheck"):
        await database.create_or_get_collection("test")
    return {"message": "OK"}
