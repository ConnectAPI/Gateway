from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends

from context import get_services
from context.docker import (
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
        return {"removed": False}
    try:
        get_services().remove_service(service_id)
    except ContainerNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='container not found')
    return {"removed": True}


@service_endpoint.put("", status_code=201)
def create(service: NewService, user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:write"])
    db = get_db()
    raise_if_service_name_if_forbidden(service.name)
    raise_if_service_name_exists(db, service.name)

    new_service_id = str(uuid4())
    while db.services.find_one({"id": new_service_id}, {"_id": 1}) is not None:
        new_service_id = str(uuid4())
    service_url = f'http://{service.name}:{service.port}'
    new_service = ServiceModel(id=new_service_id, url=service_url, **service.dict())
    service_dict = new_service.dict(escape=True)
    db.services.insert_one(service_dict)

    try:
        get_services().add_service(
            new_service_id,
            service.name,
            service_url,
            new_service.openapi_spec,
            service.image_name,
            service.environment_vars,
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
    return {"service_id": new_service_id}


@service_endpoint.get("")
def get(service_id: str, user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:read"])
    db = get_db()
    service_dict = db.services.find_one({"id": service_id}, {"_id": 0})
    if service_dict is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"service with id '{service_id}' not found")
    return ServiceModel(**service_dict).dict()


# @service_endpoint.patch("")
# def update(service_id: str, field: str, value: Any, user_scopes: list = Depends(user_permissions)):
#     raise_not_authorized(user_scopes, ["service:write", "service:delete"])
#     db = get_db()
#     if field in ("id", ):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"cant update field '{field}'")
#     service_dict = db.services.find_one({"id": service_id}, {"_id": 0})
#     service = ServiceModel(**service_dict)
#     try:
#         setattr(service, field, value)
#     except ValueError:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Field not exist or invalid value")
#
#     updated_value = service.dict(escape=True)[field]
#     updated_result = db.services.update_one({"id": service_id}, {"$set": {field: updated_value}})
#     return {"updated": updated_result.modified_count > 0}


@service_endpoint.get("/list")
def service_list(user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:read"])
    db = get_db()
    services = list(db.services.find({}, {"_id": 0, "id": 1, "name": 1}))
    return services
