from fastapi import FastAPI

from .service_discovery import service_discovery_api
from .auth import auth_api

internal_api = FastAPI(title="Internal API")

internal_api.mount('/service_discovery', service_discovery_api)
internal_api.mount('/auth', auth_api)
