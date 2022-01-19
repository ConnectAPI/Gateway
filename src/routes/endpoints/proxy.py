from urllib.parse import urljoin

from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, status, Response
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.request.datatypes import OpenAPIRequest, RequestParameters

from core.modules.services import get_services
from core.modules.auth import auth_flow
from core.settings import get_settings

proxy_endpoint = APIRouter()


def get_service(service_name: str):
    service = get_services().get_by_name(service_name)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service {service_name} not found")
    return service


def raise_on_invalid_request(request: Request, service, body):
    if service.openapi_spec:
        # Create openapi request object
        full_pattern = str(request.base_url) + str(request.path_params["p"])
        full_content_type = request.headers.get("Content-Type")
        query_params = {k: v for k, v in request.query_params.items()}
        headers = {k: v for k, v in request.headers.items() if k != get_settings().auth_token_header}

        openapi_request = OpenAPIRequest(
            full_url_pattern=full_pattern,
            method=request.method.lower(),
            body=body,
            mimetype=None if full_content_type is None else full_content_type.split(";")[0].lower(),
            parameters=RequestParameters(query=query_params, header=headers, cookie=request.cookies, path={}),
        )

        # Validate the request against the openapi spec
        if not service.openapi_spec.get("servers", None):
            service.openapi_spec["servers"] = [{"url": f"http://{request.base_url}/{service.name}"}]
        validation_response = RequestValidator(service.openapi_spec).validate(openapi_request)
        if validation_response.errors:
            response_content = [str(error) for error in validation_response.errors]
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_content)
    return True


def get_service_endpoint_required_scopes(request: Request, service_path: str, service) -> list:
    required_scopes = service.required_scopes("/" + service_path, request.method.lower())
    return required_scopes


async def forward_request(request: Request, service_path: str, body, service) -> Response:
    """ Forward the request to the service and return the response
    :param body:
    :param service_path:
    :param request: The request to forward
    :param service: the service to forward the request to (info of the service like url)
    :return: The service response
    """
    url = urljoin(service.url, service_path)
    service.client.cookies.clear()  # Do not save state for security reasons
    service.client.headers.clear()
    service_response = await service.client.request(
        request.method,
        url=url,
        data=body,
        params={k: v for k, v in request.query_params.items()},
        cookies=request.cookies,
        headers={k: v for k, v in request.headers.items()}
    )
    response = Response(
        content=service_response.content,
        status_code=service_response.status_code,
        headers={k: v for k, v in service_response.headers.items()},
    )
    return response


async def proxy_request(request: Request, bt: BackgroundTasks):
    """ Every request that need to access one of the services is going through here
    this method is responsible for validation and checking the request permissions.
    """
    requested_path = request.path_params['p']  # Example: "users/block/{userId}"
    service_path = requested_path[requested_path.find("/") + 1:]  # Example: "block/{userId}"
    service_name = requested_path.split("/")[0]  # Example: "users"
    body = (await request.body()).decode()

    service = get_service(service_name)  # Load service object
    raise_on_invalid_request(request, service, body)  # Validate the request against the service openapi spec
    required_scopes = get_service_endpoint_required_scopes(request, service_path, service)
    await auth_flow(request, required_scopes=required_scopes)  # Raises on auth exception

    response = await forward_request(request, service_path, body, service)
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
