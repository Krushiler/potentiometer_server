from pydantic import BaseModel


class Device(BaseModel):
    id: int
    name: str
    active_config: int | None
    mac_address: str
    user_id: int


class Potentiometer(BaseModel):
    id: int
    device_id: int
    name: str


class PotentiometerConfig(BaseModel):
    id: int
    value: int
    potentiometer_id: int
    config_id: int


class Config(BaseModel):
    id: int
    name: str
    device_id: int
