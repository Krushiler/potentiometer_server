from pydantic import BaseModel


class CreateDeviceRequest(BaseModel):
    name: str
    mac_address: str


class SetActiveConfigRequest(BaseModel):
    config_id: int


class CreatePotentiometerRequest(BaseModel):
    name: str
