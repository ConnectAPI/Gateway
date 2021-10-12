from typing import Dict, Any
from copy import deepcopy

from context import get_services


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
