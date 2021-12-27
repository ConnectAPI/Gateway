from urllib.parse import urljoin

from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, status, Response
from openapi_core.validation.request.validators import RequestValidator

from core.models.services import get_services
from core.models.auth import auth_flow

from ..proxy_request import ProxyRequest

proxy_endpoint = APIRouter()


def get_service(request: ProxyRequest):
    service = get_services().get_by_name(request.service_name.lower())
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return service


def raise_on_invalid_request(service, p_request: ProxyRequest):
    if service.openapi_spec:
        validation_response = RequestValidator(service.openapi_spec).validate(p_request)
        if validation_response.errors:
            response_content = [str(error) for error in validation_response.errors]
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_content)
    return True


def get_service_endpoint_required_scopes(p_request: ProxyRequest, service) -> list:
    required_scopes = service.required_scopes("/" + p_request.service_path, p_request.method.lower())
    return required_scopes


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


async def proxy_request(request: Request, bt: BackgroundTasks):
    """
    Every request that need to access one of the services is going through here
    this method is responsible for validation and checking the request permissions.
    :param bt:
    :param request:
    :return: The response from the internal service
    """
    p_request = await ProxyRequest.from_fastapi_request(request)  # The ProxyRequest object have some useful methods
    service = get_service(p_request)  # Load service object from the service_discovery service
    raise_on_invalid_request(service, p_request)  # Validate the request against the service openapi spec
    required_scopes = get_service_endpoint_required_scopes(p_request, service)
    await auth_flow(request, required_scopes=required_scopes)  # Raises on auth exception

    response = await forward_request(p_request, service)
    return response


@proxy_endpoint.get("/{p:path}", name="get", include_in_schema=False)
async def get_method_proxy(request: Request, bt: BackgroundTasks):
    return await proxy_request(request, bt)


@proxy_endpoint.post("/{p:path}", name="post", include_in_schema=False)
async def post_method_proxy(request: Request, bt: BackgroundTasks):
    return await proxy_request(request, bt)


@proxy_endpoint.put("/{p:path}", name="put", include_in_schema=False)
async def put_method_proxy(request: Request, bt: BackgroundTasks):
    return await proxy_request(request, bt)


@proxy_endpoint.delete("/{p:path}", name="delete", include_in_schema=False)
async def delete_method_proxy(request: Request, bt: BackgroundTasks):
    return await proxy_request(request, bt)


@proxy_endpoint.options("/{p:path}", name="options", include_in_schema=False)
async def options_method_proxy(request: Request, bt: BackgroundTasks):
    return await proxy_request(request, bt)


@proxy_endpoint.head("/{p:path}", name="head", include_in_schema=False)
async def head_method_proxy(request: Request, bt: BackgroundTasks):
    return await proxy_request(request, bt)


@proxy_endpoint.patch("/{p:path}", name="patch", include_in_schema=False)
async def patch_method_proxy(request: Request, bt: BackgroundTasks):
    return await proxy_request(request, bt)
