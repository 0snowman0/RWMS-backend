from pydantic import BaseModel


class TokenRequestDTO(BaseModel):
    user_id: str