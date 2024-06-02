from typing import Annotated

from fastapi import APIRouter, Depends

from data.model.device import *
from di.di import get_user_repository, get_device_repository, oauth2_scheme
from routing.device.schemes import *

router = APIRouter()


@router.put('', response_model=bool)
async def register_device(token: Annotated[str, Depends(oauth2_scheme)], request: CreateDeviceRequest,
                          auth_repo=Depends(get_user_repository),
                          device_repo=Depends(get_device_repository)):
    user = await auth_repo.get_user_by_token(token)
    await device_repo.create_device(request.name, request.mac_address, user.id)
    return True


@router.get('', response_model=list[Device])
async def get_devices(token: Annotated[str, Depends(oauth2_scheme)],
                      auth_repo=Depends(get_user_repository),
                      device_repo=Depends(get_device_repository)):
    user = await auth_repo.get_user_by_token(token)
    return await device_repo.get_devices(user.id)


@router.patch('/{device_id}', response_model=bool)
async def set_active_config(token: Annotated[str, Depends(oauth2_scheme)], device_id: int,
                            request: SetActiveConfigRequest,
                            device_repo=Depends(get_device_repository)):
    await device_repo.set_active_config(device_id, request.config_id)
    return True


@router.put('/{device_id}/potentiometers', response_model=bool)
async def register_potentiometer(token: Annotated[str, Depends(oauth2_scheme)], device_id: int,
                                 request: CreatePotentiometerRequest,
                                 device_repo=Depends(get_device_repository)):
    await device_repo.create_potentiometer(request.name, device_id)
    return True


@router.get('/{device_id}/potentiometers', response_model=list[Potentiometer])
async def get_potentiometers(token: Annotated[str, Depends(oauth2_scheme)], device_id: int,
                             device_repo=Depends(get_device_repository)):
    return await device_repo.get_potentiometers(device_id)
