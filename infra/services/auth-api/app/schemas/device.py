from pydantic import BaseModel, Field

class DeviceBase(BaseModel):
    name: str = Field(..., max_length=64)

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    name: str | None = Field(None, max_length=64)
    status: str | None = Field(None, max_length=16)

class DeviceOut(DeviceBase):
    id: int
    tenant_id: int
    status: str

    class Config:
        orm_mode = True
