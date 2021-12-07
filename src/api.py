from fastapi import FastAPI

from core.models.db import get_db
from core.models.cache import get_cache

from external_api import proxy_router
from internal_api import internal_api
from internal_api.service_discovery import get_services
from internal_api.service_discovery.openapi import openapi_schema


app = FastAPI(title="Gateway")
app.mount("/internal", internal_api)
app.openapi = openapi_schema

app.include_router(proxy_router)


@app.on_event("startup")
async def startup():
    get_db()
    get_cache()
    get_services()


@app.on_event("shutdown")
async def shutdown():
    get_db().close()
    get_cache().close()
    get_services().shutdown()
