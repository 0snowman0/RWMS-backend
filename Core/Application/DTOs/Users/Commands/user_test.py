from pydantic import BaseModel


class UserDto(BaseModel):
    email: str
    full_name: str
    is_active: bool


class UserCustomDto(BaseModel):
    email: str
    name: str
    status: str    
    