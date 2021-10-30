from typing import Dict, Any
from copy import deepcopy

from fastapi import Request as FastAPIRequest, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from openapi_core.validation.request.validators import RequestValidator

from context import get_services
from models.request import Request
from .security import auth_flow


def get_service(request: FastAPIRequest):
    services = get_services()
    service_prefix_path = request.path_params["p"].split("/")[0]
    service = services.get_service(service_prefix_path.lower())
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return service


def get_required_scopes(r: FastAPIRequest, service):
    full_path = r.path_params['p']
    service_path = full_path[r.path_params['p'].find(service.prefix_path) + len(service.prefix_path):]
    scopes = service.get_required_scopes(service_path, r.method.lower())
    return scopes


async def get_token(request: FastAPIRequest, required_scopes: list):
    json_token: dict = await auth_flow(request, required_scopes=required_scopes)
    return json_token


async def is_valid_request(service, request):
    print(service.openapi_spec, bool(service.openapi_spec), service.__dict__)
    if service.openapi_spec:
        validation_response = RequestValidator(service.openapi_spec).validate(request)
        print(validation_response.errors)
        if validation_response.errors:
            response_content = [str(error) for error in validation_response.errors]
            return JSONResponse(content=response_content, status_code=400)
    return True


def openapi_schema():
    services = get_services()
    merged_schema: Dict[str, Any] = {
        "openapi": "3.0.2",
        "info": {
                "title": "APIGateway",
                "version": "0.1.0"
            },
        "servers": [],
        "security": [
            {"auth": []}
        ],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {
                "auth": {
                    "type": "oauth2",
                    "flows": {
                        "password": {
                                "scopes": {},
                                "tokenUrl": "internal/auth/token",
                                "refreshUrl": "internal/auth/refresh_token",
                            }
                    }
                }
            }
        },
    }
    for service in services:
        schema = deepcopy(service.openapi_dict)
        for path, data in schema["paths"].items():
            for operation in data.values():
                operation.pop("tags", None)
                operation["tags"] = [service.name]
            merged_schema["paths"]['/' + service.prefix_path + path] = data
        merged_schema["components"]["schemas"].update(schema.get("components", {}).get("schemas"))
    return merged_schema
