from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

from core.modules.db import get_db
from core.modules.cache import get_cache
from core.modules.services import get_services, openapi_schema

from routes import proxy_router, internal_app


app = FastAPI(title="Gateway")
app.mount("/internal", internal_app)
app.add_middleware(PrometheusMiddleware)

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
