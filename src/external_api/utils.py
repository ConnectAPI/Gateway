from copy import deepcopy

from context import get_services
from .config import EXTERNAL_PREFIX


def openapi_schema():
    services = get_services()
    merged_schema = {
        "openapi": "3.0.2",
        "info": {
                "title": "APIGateway",
                "version": "0.1.0"
            },
        "servers": [
            {"url": EXTERNAL_PREFIX}
        ],
        "security": [
            {
                "api_auth": []
            }
        ],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {
                "api_auth": {
                    "type": "oauth2",
                    "flows": {
                        "password": {
                                "scopes": {},
                                "tokenUrl": "auth/token",
                                "refreshUrl": "auth/refresh_token",
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
                scope = f"{service.prefix_path}:{path[1:]}"
                scope_description = f"Access to {service.prefix_path} endpoint {path[1:]}"
                operation["security"] = [{"api_auth": [scope]}]
                merged_schema["components"]["securitySchemes"]["api_auth"]["flows"]["password"]["scopes"][scope]\
                    = scope_description

            merged_schema["paths"]['/' + service.prefix_path + path] = data
        merged_schema["components"]["schemas"].update(schema.get("components", {}).get("schemas"))
    return merged_schema
