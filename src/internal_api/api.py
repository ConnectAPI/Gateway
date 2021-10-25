from fastapi import FastAPI, Request, Response, HTTPException, status
import httpx

from context import get_services, get_settings

internal_api = FastAPI(title="Internal API")


INTERNAL_SERVICES_PRODUCTION = {
    "auth": "http://core-auth",
    "service_discovery": "http://core-service-discovery"
}

INTERNAL_SERVICES_DEVELOPMENT = {
    "auth": "http://127.0.0.2",
    "service_discovery": "http://127.0.0.3"
}


def update_services():
    services = get_services()
    services.reload()


@internal_api.route("/{service:str}/{p:path}", methods=["GET", "POST", "DELETE", "PUT"])
async def service_proxy(r: Request):
    service = r.path_params["service"]
    internal_services_url = INTERNAL_SERVICES_PRODUCTION \
        if get_settings().env == "PRODUCTION" else INTERNAL_SERVICES_DEVELOPMENT
    try:
        async with httpx.AsyncClient() as client:
            service_response = await client.request(
                    method=r.method.lower(),
                    url=f"{internal_services_url[service]}/{r.path_params['p']}",
                    params=r.query_params,
                    cookies=r.cookies,
                    headers=r.headers,
                    data=await r.body()
                )
    except (ConnectionError, httpx.ConnectError):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    response = Response(
        content=service_response.content,
        status_code=service_response.status_code,
        headers={k: v for k, v in service_response.headers.items()},
    )

    if service == "service_discovery":  # This is a hack, I know! and it will probably will never get fixed
        if response.status_code < 300 and r.method.lower() != "get":
            update_services()
    return response
