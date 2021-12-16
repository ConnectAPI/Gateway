from datetime import datetime
import json

from openapi_spec_validator import validate_spec
from openapi_spec_validator.validators import OpenAPIValidationError
from pydantic import BaseModel, constr, Field, AnyHttpUrl, validator


class NewService(BaseModel):
    id: constr(max_length=100)
    name: constr(max_length=40)
    image_name: str
    environment_vars: dict = Field(default_factory=dict)
    openapi_spec: dict
    port: int = Field(default=80)

    @validator('port')
    def validate_port(cls, port):
        if port < 1 or port > 65535:
            raise ValueError(f"Invalid port number <{port}>")
        return port

    @validator("openapi_spec")
    def validate_openapi_spec(cls, spec):
        try:
            validate_spec(spec=spec)
        except OpenAPIValidationError:
            raise ValueError("Invalid openapi spec")
        return spec


class ServiceModel(BaseModel):
    id: str
    name: str
    image_name: str
    url: AnyHttpUrl
    environment_vars: dict
    openapi_spec: dict
    port: int
    created_at: datetime = Field(default_factory=datetime.utcnow, description="creation time in UTC timezone")

    @validator("openapi_spec", whole=True, pre=True)
    def convert_spec_to_dict(cls, spec):
        if type(spec) is not dict:
            spec = json.loads(spec)
        return spec

    def dict(self, escape: bool = False, *args, **kwargs):
        dict_res = super().dict(*args, **kwargs)
        if escape:
            dict_res["openapi_spec"] = json.dumps(dict_res["openapi_spec"])
        return dict_res

