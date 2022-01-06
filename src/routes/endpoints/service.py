from fastapi import APIRouter, HTTPException, status, Request

from core.modules.services import get_services
from core.modules.services.docker import (
    NotAuthorizedContainer,
    ContainerNotFound,
    ContainerAllReadyRunning,
    ImageNotFound,
)

from core.modules.db import get_db
from core.schemas.service import NewService, ServiceModel
from core.modules.auth import auth_flow

service_router = APIRouter(prefix="/service", tags=["service"])


FORBIDDEN_SERVICE_NAMES = ['internal']


def raise_if_service_name_exists(db, service_name):
    if db.services.find_one({"name": service_name}, {"_id": 1}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name are all ready exist.")


def raise_if_service_name_if_forbidden(service_name):
    if service_name.lower() in FORBIDDEN_SERVICE_NAMES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="service name is forbidden."
        )


@service_router.delete("")
async def remove(r: Request, service_id: str):
    db = get_db()
    await auth_flow(r, required_scopes=["service:delete"])

    service = db.services.find_one_and_delete({"id": service_id})
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service with id {service_id} not found")
    try:
        get_services().remove(service_id)
    except ContainerNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='service not found')
    return {"removed": True}


@service_router.put("", status_code=201)
async def create(r: Request, service: NewService):
    db = get_db()
    await auth_flow(r, required_scopes=["service:write"])

    raise_if_service_name_if_forbidden(service.name)
    raise_if_service_name_exists(db, service.name)

    service_url = f'http://{service.name.replace(" ", "_")}:{service.port}'
    new_service = ServiceModel(url=service_url, **service.dict())
    service_dict = new_service.dict(escape=True)
    db.services.insert_one(service_dict)

    try:
        get_services().add(
            service.id,
            service.name,
            service_url,
            new_service.openapi_spec,
            service.image_name,
            service.environment_vars,
        )
    except NotAuthorizedContainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Image name is not from connectapisys docker hub account."
        )
    except ContainerAllReadyRunning:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Container with that name ('{service.name}') is all ready running."
        )
    except ImageNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service image ('{service.image_name}') not found."
        )
    return {"service_id": service.id}


@service_router.get("")
async def get(r: Request, service_id: str):
    db = get_db()
    await auth_flow(r, required_scopes=["service:read"])

    service_dict = db.services.find_one({"id": service_id}, {"_id": 0})
    if service_dict is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service with id '{service_id}' not found")
    return ServiceModel(**service_dict).dict()


@service_router.post("/pause")
async def pause(r: Request, service_id: str):
    await auth_flow(r, required_scopes=["service:delete"])

    get_services().pause(service_id)
    return {"pause": True}


@service_router.post("/unpause")
async def unpause(r: Request, service_id: str):
    await auth_flow(r, required_scopes=["service:delete"])

    get_services().unpause(service_id)
    return {"unpause": True}


@service_router.get("/list")
async def service_list(r: Request):
    db = get_db()
    await auth_flow(r, required_scopes=["service:delete"])

    services = list(db.services.find({}, {"_id": 0, "id": 1, "name": 1}))
    return services
