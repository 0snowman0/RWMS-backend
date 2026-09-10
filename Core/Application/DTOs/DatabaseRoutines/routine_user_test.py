from pydantic import BaseModel


class RoutineUserDto(BaseModel):

    id: int
    email: str
    full_name: str
    is_active: bool