from urllib.parse import urljoin

from fastapi import APIRouter, Response, Request as FastAPIRequest

from models.request import Request

from ..utils import get_service, is_valid_request, get_token, get_required_scopes


ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]


proxy_endpoint = APIRouter()


async def proxy_request(request: FastAPIRequest):
    service = get_service(request)
    required_scopes = get_required_scopes(request, service)
    request = await Request.from_fastapi_request(request)
    token = get_token(request, required_scopes)
    valid_request = is_valid_request(service, request)

    url = urljoin(service.url, request.service_path)
    service.client.cookies.clear()  # Do not save state for security reasons
    service.client.headers.clear()
    service_response = await service.client.request(
        request.method,
        url=url,
        params=request.parameters.query,
        cookies=request.cookies,
        headers={k: v for k, v in request.headers.items()}
    )
    response_content = service_response.content
    response = Response(
        content=response_content,
        status_code=service_response.status_code,
        headers={k: v for k, v in service_response.headers.items()},
    )
    return response


@proxy_endpoint.get("/{p:path}", name="get", include_in_schema=False)
async def get_method_proxy(request: FastAPIRequest):
    return await proxy_request(request)


@proxy_endpoint.post("/{p:path}", name="post", include_in_schema=False)
async def post_method_proxy(request: FastAPIRequest):
    return await proxy_request(request)


@proxy_endpoint.put("/{p:path}", name="put", include_in_schema=False)
async def put_method_proxy(request: FastAPIRequest):
    return await proxy_request(request)


@proxy_endpoint.delete("/{p:path}", name="delete", include_in_schema=False)
async def delete_method_proxy(request: FastAPIRequest):
    return await proxy_request(request)


@proxy_endpoint.options("/{p:path}", name="options", include_in_schema=False)
async def options_method_proxy(request: FastAPIRequest):
    return await proxy_request(request)


@proxy_endpoint.head("/{p:path}", name="head", include_in_schema=False)
async def head_method_proxy(request: FastAPIRequest):
    return await proxy_request(request)


@proxy_endpoint.patch("/{p:path}", name="patch", include_in_schema=False)
async def patch_method_proxy(request: FastAPIRequest):
    return await proxy_request(request)
