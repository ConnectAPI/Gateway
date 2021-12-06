from fastapi import Request as FastAPIRequest, HTTPException, status
from openapi_core.validation.request.validators import RequestValidator

from internal_api.service_discovery import get_services
from core.models.request import Request

from .security import auth_flow


def get_service(request: FastAPIRequest):
    service_prefix_path = request.path_params["p"].split("/")[0]
    service = get_services().get_by_prefix_path(service_prefix_path.lower())
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return service


def get_required_scopes(r: FastAPIRequest, service):
    full_path = r.path_params['p']
    service_path = full_path[r.path_params['p'].find(service.prefix_path) + len(service.prefix_path):]
    scopes = service.required_scopes(service_path, r.method.lower())
    return scopes


async def get_token(request: FastAPIRequest, required_scopes: list):
    json_token: dict = await auth_flow(request, required_scopes=required_scopes)
    return json_token


async def is_valid_request(service, request: Request):
    if service.openapi_spec:
        validation_response = RequestValidator(service.openapi_spec).validate(request)
        if validation_response.errors:
            response_content = [str(error) for error in validation_response.errors]
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response_content)
    return True
