from fastapi.security import OAuth2PasswordBearer

from config import DB_FILE_NAME
from data.repository.device_repository import DeviceRepository
from data.repository.user_repository import UserRepository


def get_user_repository() -> UserRepository:
    repository = UserRepository(DB_FILE_NAME)
    try:
        yield repository
    finally:
        repository.close()


def get_device_repository() -> DeviceRepository:
    repository = DeviceRepository(DB_FILE_NAME)
    try:
        yield repository
    finally:
        repository.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")
