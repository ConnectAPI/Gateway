from urllib.parse import urljoin

from fastapi import Request, HTTPException, status, Response
from openapi_core.validation.request.validators import RequestValidator

from internal_api.service_discovery import get_services

from .proxy_request import ProxyRequest
from .security import auth_flow


def get_service(request: ProxyRequest):
    service = get_services().get_by_name(request.service_name.lower())
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return service


def _get_required_scopes(r: Request, service):
    full_path = r.path_params['p']
    service_path = full_path[r.path_params['p'].find(service.prefix_path) + len(service.prefix_path):]
    scopes = service.required_scopes(service_path, r.method.lower())
    return scopes


async def raise_on_insufficient_permissions(request: Request, service):
    required_scopes = _get_required_scopes(request, service)
    json_token: dict = await auth_flow(request, required_scopes=required_scopes)
    return json_token


async def raise_on_invalid_request(service, p_request: ProxyRequest):
    if service.openapi_spec:
        validation_response = RequestValidator(service.openapi_spec).validate(p_request)
        if validation_response.errors:
            response_content = [str(error) for error in validation_response.errors]
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response_content)
    return True


async def forward_request(p_request, service) -> Response:
    """ Forward the request to the service and return the response
    :param p_request: The request to forward
    :param service: the service to forward the request to (info of the service like url)
    :return: The service response
    """
    url = urljoin(service.url, p_request.service_path)
    service.client.cookies.clear()  # Do not save state for security reasons
    service.client.headers.clear()
    service_response = await service.client.request(
        p_request.method,
        url=url,
        data=p_request.body,
        params=p_request.parameters.query,
        cookies=p_request.cookies,
        headers={k: v for k, v in p_request.headers.items()}
    )
    response_content = service_response.content
    response = Response(
        content=response_content,
        status_code=service_response.status_code,
        headers={k: v for k, v in service_response.headers.items()},
    )
    return response
