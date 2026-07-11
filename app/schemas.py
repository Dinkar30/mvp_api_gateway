from pydantic import BaseModel

class ServiceCreate(BaseModel):
    name:str
    prefix: str
    target_url: str
    healthcheck_path: str = "/"

    class Config:
        from_attributes=True

class ServiceResponse(ServiceCreate):
    id: int


class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"