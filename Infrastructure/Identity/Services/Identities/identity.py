from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import Response
from jose import jwt
from Core.Application.Contracts.Identities.identity import ITokenService
from Core.Application.DTOs.Identities.Commands.token import SetCookieTokenDTO, TokenRequestDTO, RefreshTokenRequestDTO
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

    def set_tokens_in_cookies(
        self,
        response: Response,
        request: SetCookieTokenDTO
    ) -> None:

        response.set_cookie(
            key="access_token",
            value=request.access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=self.access_expire_minutes * 60,
            path="/"
        )

        response.set_cookie(
            key="refresh_token",
            value=request.refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=self.refresh_expire_minutes * 60,
            path="/"
        )

    def clear_tokens_from_cookies(
        self,
        response: Response
    ) -> None:

        response.delete_cookie(
            key="access_token",
            path="/"
        )

        response.delete_cookie(
            key="refresh_token",
            path="/"
        )

    def decode_token(
        self,
        token: str
    ) -> dict[str, Any]:

        payload = jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm],
            issuer="my-fastapi-app"
        )

        return payload