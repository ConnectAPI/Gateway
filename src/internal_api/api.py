from fastapi import FastAPI, Request, Response
from httpx import AsyncClient

from context import get_services

internal_api = FastAPI(title="Internal API")


INTERNAL_SERVICES = {
    "auth": "http://127.0.0.3:120",
    "service_discovery": "http://127.0.0.4:121"
}


def auth_client() -> AsyncClient:
    return AsyncClient()


def update_services():
    services = get_services()
    services.reload()


@internal_api.route("/{service:str}/{p:path}", methods=["GET", "POST", "DELETE", "PUT"])
async def service_proxy(r: Request):
    service = r.path_params["service"]
    async with AsyncClient() as client:
        service_response = await client.request(
                method=r.method.lower(),
                url=f"{INTERNAL_SERVICES[service]}/{r.path_params['p']}",
                params=r.query_params,
                cookies=r.cookies,
                data=await r.body()
            )
    response = Response(
        content=service_response.content,
        status_code=service_response.status_code,
        headers={k: v for k, v in service_response.headers.items()},
    )

    if service == "service_discovery":  # This is a hack, I know! and it will probably will never get fixed
        if response.status_code < 300 and r.method.lower() != "get":
            update_services()
    return response
