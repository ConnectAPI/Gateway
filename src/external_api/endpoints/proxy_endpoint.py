from fastapi import APIRouter, Request

from ..proxy_request import ProxyRequest

from ..utils import (
    get_service,
    raise_on_invalid_request,
    raise_on_insufficient_permissions,
    forward_request,
)

proxy_endpoint = APIRouter()


async def proxy_request(request: Request):
    """
    Every request that need to access one of the services is going through here
    this method is responsible for validation and checking the request permissions.
    :param request:
    :return: The response from the internal service
    """
    p_request = await ProxyRequest.from_fastapi_request(request)  # The ProxyRequest object have some useful methods
    service = get_service(p_request)  # Load service object from the service_discovery service
    await raise_on_invalid_request(service, p_request)  # Validate the request against the service openapi spec

    # Check if the request jwt key have the needed permissions
    await raise_on_insufficient_permissions(request, service)

    response = await forward_request(p_request, service)
    return response


@proxy_endpoint.get("/{p:path}", name="get", include_in_schema=False)
async def get_method_proxy(request: Request):
    return await proxy_request(request)


@proxy_endpoint.post("/{p:path}", name="post", include_in_schema=False)
async def post_method_proxy(request: Request):
    return await proxy_request(request)


@proxy_endpoint.put("/{p:path}", name="put", include_in_schema=False)
async def put_method_proxy(request: Request):
    return await proxy_request(request)


@proxy_endpoint.delete("/{p:path}", name="delete", include_in_schema=False)
async def delete_method_proxy(request: Request):
    return await proxy_request(request)


@proxy_endpoint.options("/{p:path}", name="options", include_in_schema=False)
async def options_method_proxy(request: Request):
    return await proxy_request(request)


@proxy_endpoint.head("/{p:path}", name="head", include_in_schema=False)
async def head_method_proxy(request: Request):
    return await proxy_request(request)


@proxy_endpoint.patch("/{p:path}", name="patch", include_in_schema=False)
async def patch_method_proxy(request: Request):
    return await proxy_request(request)
