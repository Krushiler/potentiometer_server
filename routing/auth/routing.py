from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from di.di import get_user_repository

router = APIRouter()


@router.post('')
async def authenticate(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                       repository=Depends(get_user_repository)):
    return {'access_token': await repository.authenticate(form_data.username, form_data.password),
            'token_type': 'bearer'}
