from pydantic import BaseModel

class ServiceCreate(BaseModel):
    name:str
    prefix: str
    target_url: str

    class Config:
        from_attributes=True

class ServiceResponse(ServiceCreate):
    id: int

