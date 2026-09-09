from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import Response
from jose import ExpiredSignatureError, jwt
from Core.Application.Contracts.Identities.identity import ITokenService
from Core.Application.DTOs.Identities.Commands.token import SetCookieTokenDTO, TokenRequestDTO, RefreshTokenRequestDTO, TokenValidationError, TokenValidationResultDTO
from Configs.Identities.identity import settings
from jose.exceptions import (
    ExpiredSignatureError,
    JWTError,
    JWTClaimsError,
)

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
            "sub": str(request.user_id),
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
            "sub": str(request.user_id),
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

    def validate_token(
        self,
        token: str
    ) -> TokenValidationResultDTO:

        try:
            jwt.get_unverified_header(token)
            jwt.get_unverified_claims(token)

        except JWTError:
            return TokenValidationResultDTO(
                is_valid=False,
                error=TokenValidationError.MALFORMED,
                message="Token is malformed"
            )

        try:

            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer="my-fastapi-app"
            )

            return TokenValidationResultDTO(
                is_valid=True,
                error=None,
                message=None,
                payload=payload
            )

        except ExpiredSignatureError:

            return TokenValidationResultDTO(
                is_valid=False,
                error=TokenValidationError.EXPIRED,
                message="Token has expired"
            )

        except JWTClaimsError:

            return TokenValidationResultDTO(
                is_valid=False,
                error=TokenValidationError.INVALID,
                message="Token claims are invalid"
            )

        except JWTError:

            return TokenValidationResultDTO(
                is_valid=False,
                error=TokenValidationError.TAMPERED,
                message="Token signature is invalid or token has been tampered with"
            )
