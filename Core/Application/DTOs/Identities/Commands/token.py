from enum import Enum
from typing import Any

from pydantic import BaseModel


class TokenRequestDTO(BaseModel):
    user_id: str
    
class RefreshTokenRequestDTO(BaseModel):    
    user_id: str
    
class SetCookieTokenDTO(BaseModel):
    access_token: str
    refresh_token: str    

class TokenValidationError(str, Enum):
    EXPIRED = "expired"
    TAMPERED = "tampered"
    MALFORMED = "malformed"
    INVALID = "invalid"
    
class TokenValidationResultDTO(BaseModel):
    is_valid: bool
    error: TokenValidationError | None = None    
    message: str | None = None
    payload: dict[str, Any] | None = None

    