from pydantic import BaseModel


class AuthenticateRequest(BaseModel):
    login: str
    password: str
