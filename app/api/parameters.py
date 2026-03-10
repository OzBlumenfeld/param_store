from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging
from typing import Optional, Any
from app.core.database import get_db
from app.services.parameter_service import ParameterService
from app.services.encryption import EncryptionService
from app.core.config import settings
from app.api.auth import get_current_user
from app.models.user import User

# Using the "params" logger
logger = logging.getLogger("params")

# prefix="/params" sets the base path for all routes in this router
router = APIRouter(prefix="/params", tags=["parameters"])


class ParameterRequest(BaseModel):
    app: str = Field("default", max_length=255)
    name: str = Field(..., max_length=255)
    value: str


class ParameterUpdateRequest(BaseModel):
    value: str



class ParameterResponse(BaseModel):
    name: str
    message: str


def get_parameter_service(db: Session = Depends(get_db)) -> ParameterService:
    encryption_service = EncryptionService(settings.MASTER_ENCRYPTION_KEY)
    return ParameterService(db, encryption_service)


@router.post("/", response_model=ParameterResponse)
async def set_param(
    req: ParameterRequest, 
    current_user: User = Depends(get_current_user),
    service: ParameterService = Depends(get_parameter_service)
) -> ParameterResponse:
    """Stores a parameter securely with envelope encryption."""
    logger.info("Setting parameter", extra={"param_name": req.name, "user": current_user.username})
    try:
        service.set_parameter(current_user.id, req.app, req.name, req.value)
        return ParameterResponse(name=req.name, message="Parameter saved successfully")
    except Exception as e:
        logger.error("Failed to set parameter", extra={"param_name": req.name, "error": str(e)})
        raise HTTPException(
            status_code=500, detail=f"Failed to save parameter: {str(e)}"
        )


@router.put("/{name}", response_model=ParameterResponse)
async def update_param(
    name: str,
    req: ParameterUpdateRequest,
    app: str = "default",
    current_user: User = Depends(get_current_user),
    service: ParameterService = Depends(get_parameter_service)
) -> ParameterResponse:
    """Updates an existing parameter securely."""
    logger.info("Updating parameter", extra={"param_name": name, "user": current_user.username})
    try:
        updated_param = service.update_parameter(current_user.id, app, name, req.value)
        if not updated_param:
            logger.warning("Parameter not found for update", extra={"param_name": name})
            raise HTTPException(status_code=404, detail="Parameter not found")
        return ParameterResponse(name=name, message="Parameter updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update parameter", extra={"param_name": name, "error": str(e)})
        raise HTTPException(
            status_code=500, detail=f"Failed to update parameter: {str(e)}"
        )


@router.get("/")
async def list_params(
    app: Optional[str] = None,
    name: Optional[str] = None,
    get_all_values: bool = False,
    current_user: User = Depends(get_current_user),
    service: ParameterService = Depends(get_parameter_service)
) -> list[dict[str, str]]:
    """Retrieves all parameter names for the current user."""
    return service.get_parameters_for_user(current_user.id, app=app, name=name, get_all_values=get_all_values)


@router.get("/{name}")
async def get_param(
    name: str, 
    app: str = "default",
    current_user: User = Depends(get_current_user),
    service: ParameterService = Depends(get_parameter_service)
) -> dict[str, str]:
    """Retrieves and decrypts a parameter."""
    logger.info("Retrieving parameter", extra={"param_name": name, "user": current_user.username})
    value = service.get_parameter(current_user.id, name, app)
    if value is None:
        logger.warning("Parameter not found", extra={"param_name": name})
        raise HTTPException(status_code=404, detail="Parameter not found")
    return {"name": name, "value": value}


@router.delete("/{name}")
async def delete_param(
    name: str, 
    app: str = "default",
    current_user: User = Depends(get_current_user),
    service: ParameterService = Depends(get_parameter_service)
):
    """Deletes a parameter."""
    logger.info("Deleting parameter", extra={"param_name": name, "user": current_user.username})
    success = service.delete_param(current_user.id, name, app)
    if not success:
        logger.warning("Parameter not found for deletion", extra={"param_name": name})
        raise HTTPException(status_code=404, detail="Parameter not found")
    return {"name": name, "message": "Parameter deleted successfully"}
