from pydantic import BaseModel


class TokenRequestDTO(BaseModel):
    user_id: str
    
class RefreshTokenRequestDTO(BaseModel):    
    user_id: str
    
class SetCookieTokenDTO(BaseModel):
    access_token: str
    refresh_token: str    
    