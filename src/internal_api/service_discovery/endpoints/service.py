from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends

from ..core.models.services import get_services
from ..core.models.docker import (
    NotAuthorizedContainer,
    ContainerNotFound,
    ContainerAllReadyRunning,
    ImageNotFound,
)

from ..core.models.db import get_db
from ..core.schemas.service import NewService, ServiceModel
from ..autherization import user_permissions, raise_not_authorized
from .validations import raise_if_service_name_exists, raise_if_service_name_if_forbidden

service_endpoint = APIRouter(prefix="/service", tags=["service"])


@service_endpoint.delete("")
def remove(service_id: str, user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:delete"])
    db = get_db()
    service = db.services.find_one_and_delete({"id": service_id})
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service with id {service_id} not found")
    try:
        get_services().remove(service_id)
    except ContainerNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='service not found')
    return {"removed": True}


@service_endpoint.put("", status_code=201)
def create(service: NewService, user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:write"])
    db = get_db()
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
            service.port
        )
    except NotAuthorizedContainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Image name is not from boxs docker hub account."
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


@service_endpoint.get("")
def get(service_id: str, user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:read"])
    db = get_db()
    service_dict = db.services.find_one({"id": service_id}, {"_id": 0})
    if service_dict is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service with id '{service_id}' not found")
    return ServiceModel(**service_dict).dict()


@service_endpoint.post("/pause")
def pause(service_id: str, user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:delete"])
    get_services().pause(service_id)
    return {"pause": True}


@service_endpoint.post("/unpause")
def pause(service_id: str, user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:delete"])
    get_services().pause(service_id)
    return {"unpause": True}


@service_endpoint.get("/list")
def service_list(user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:read"])
    db = get_db()
    services = list(db.services.find({}, {"_id": 0, "id": 1, "name": 1}))
    return services
