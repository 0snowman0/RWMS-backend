from datetime import datetime, timedelta, timezone
from jose import jwt
from Core.Application.Contracts.Identities.identity import ITokenService
from Core.Application.DTOs.Identities.Commands.token import TokenRequestDTO
from Configs.Identities.identity import settings


class JWTTokenService(ITokenService):

    def __init__(self):
        self.secret_key = settings.identity.SECRET_KEY
        self.algorithm = settings.identity.ALGORITHM
        self.access_expire_minutes = settings.identity.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, request: TokenRequestDTO) -> str:        
        expiration = datetime.now(timezone.utc) + timedelta(minutes=self.access_expire_minutes)
        
        payload = {
            "user_id": request.user_id,
            "expiration": expiration.isoformat(),
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "issuer": "my-fastapi-app",
            "token_type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)