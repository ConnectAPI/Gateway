from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends

from context import get_services
from models.service import Service

from ..core.models.db import get_db
from ..core.schemas.service import NewService, ServiceModel
from ..core.models.docker import docker_client, NotAuthorizedContainer
from ..autherization import user_permissions, raise_not_authorized

service_endpoint = APIRouter(prefix="/service", tags=["service"])


@service_endpoint.delete("")
def remove(service_id: str, user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:delete"])
    db = get_db()
    service = db.services.find_one_and_delete({"id": service_id})
    if service is not None:
        get_services().remove_service(service_id)
        docker_client().stop_container(service['name'])
    return {"removed": service is not None}


@service_endpoint.put("", status_code=201)
def create(service: NewService, user_scopes: list = Depends(user_permissions)):
    raise_not_authorized(user_scopes, ["service:write"])
    db = get_db()
    if db.services.find_one({"name": service.name}, {"_id": 1}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name are all ready exist.")
    new_service_id = str(uuid4())
    while db.services.find_one({"id": new_service_id}, {"_id": 1}) is not None:
        new_service_id = str(uuid4())
    try:
        container, container_url = docker_client().run_container(
            service.image_name,
            service.environment_vars,
            service.name,
            service.port,
        )
    except NotAuthorizedContainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Image name is not from boxs docker hub account."
        )

    new_service = ServiceModel(id=new_service_id, container_id=container.id, url=container_url, **service.dict())
    service_dict = new_service.dict(escape=True)
    db.services.insert_one(service_dict)
    new_system_service = Service(new_service_id, service.name, new_service.url, new_service.openapi_spec)
    get_services().add_service(new_system_service)
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
