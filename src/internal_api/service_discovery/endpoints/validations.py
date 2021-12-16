from fastapi import HTTPException, status


FORBIDDEN_SERVICE_NAMES = ['internal']


def raise_if_service_name_exists(db, service_name):
    db.services.delete_many({})
    if db.services.find_one({"name": service_name}, {"_id": 1}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name are all ready exist.")


def raise_if_service_name_if_forbidden(service_name):
    if service_name.lower() in FORBIDDEN_SERVICE_NAMES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="service name is forbidden."
        )
