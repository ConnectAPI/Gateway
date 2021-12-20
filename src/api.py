from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

from core.models.db import get_db
from core.models.cache import get_cache

from external_api import proxy_router
from internal_api import internal_api
from internal_api.service_discovery import get_services
from internal_api.service_discovery.openapi import openapi_schema


app = FastAPI(title="Gateway")
app.add_middleware(PrometheusMiddleware, group_paths=True)
app.mount("/internal", internal_api)

app.add_route("/metrics", handle_metrics)
app.include_router(proxy_router)

app.openapi = openapi_schema


@app.on_event("startup")
async def startup():
    get_db()
    get_cache()
    get_services().load_services()


@app.on_event("shutdown")
async def shutdown():
    get_db().close()
    get_cache().close()
    get_services().shutdown()
