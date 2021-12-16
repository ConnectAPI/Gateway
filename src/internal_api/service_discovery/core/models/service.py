import json

from openapi_core import create_spec
import httpx


class Service:
    def __init__(
            self,
            id: str,
            name: str,
            url: str,
            openapi_dict: dict,
            image_name: str,
            environment_vars: dict,
            **kwargs,
    ):
        self.id: str = id
        self.name = name
        self.url = url
        self.openapi_dict = openapi_dict
        self.image_name = image_name
        self.environment_vars = environment_vars

        self.openapi_spec = self._build_openapi_spec()
        self.client = httpx.AsyncClient()

    def required_scopes(self, path: str, operation: str) -> list:
        operation = self.openapi_dict["paths"][path][operation]
        if not operation.get("security", []):
            return []
        return list(operation["security"][0].values())

    def _build_openapi_spec(self):
        self.openapi_dict["servers"] = [{"url": f"http://boxs.ml/{self.name.lower()}"}]
        openapi_spec = create_spec(self.openapi_dict)
        return openapi_spec

    @classmethod
    def from_dict(cls, service_dict: dict):
        if type(service_dict.get("openapi_spec", None)) is str:
            service_dict["openapi_spec"] = json.loads(service_dict["openapi_spec"])
        service_dict["openapi_dict"] = service_dict.pop("openapi_spec")
        return cls(**service_dict)
