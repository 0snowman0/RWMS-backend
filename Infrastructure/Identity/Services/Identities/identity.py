from datetime import datetime, timedelta, timezone
from jose import jwt
from Core.Application.Contracts.Identities.identity import ITokenService
from Core.Application.DTOs.Identities.Commands.token import TokenRequestDTO, RefreshTokenRequestDTO
from Configs.Identities.identity import settings


class JWTTokenService(ITokenService):

    def __init__(self):
        self.secret_key = settings.identity.SECRET_KEY
        self.algorithm = settings.identity.ALGORITHM
        self.access_expire_minutes = settings.identity.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_expire_minutes = settings.identity.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
    
    def create_access_token(self, request: TokenRequestDTO) -> str:        
        now = datetime.now(timezone.utc)
        expiration = now + timedelta(minutes=self.access_expire_minutes)
        
        payload = {
            "sub": request.user_id,
            "exp": expiration,  
            "iat": now,
            "iss": "my-fastapi-app",
            "token_type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, request: RefreshTokenRequestDTO) -> str:
        now = datetime.now(timezone.utc)
        expiration = now + timedelta(minutes=self.refresh_expire_minutes)
        
        payload = {
            "sub": request.user_id,
            "exp": expiration,
            "iat": now,
            "iss": "my-fastapi-app",
            "token_type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)