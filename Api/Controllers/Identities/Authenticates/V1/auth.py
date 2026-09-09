# Api/Controllers/Identity/Auth/V1/Authenticates.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from Core.Application.DTOs.Identities.Commands.token import RefreshTokenRequestDTO, SetCookieTokenDTO, TokenRequestDTO
from Core.Application.Contracts.Identities.identity import ITokenService
from Configs.dependencies import TokenServiceDependency, get_token_service  
from jose import jwt
router = APIRouter(tags=["Authenticates"])

@router.post("/create-token")
async def create_token(
    request: TokenRequestDTO,
    token_service: TokenServiceDependency
):
    token = token_service.create_access_token(request)
    return {
        "message": "Token created successfully",
        "access_token": token,
        "token_type": "Bearer"
    }

@router.post("/refresh-token")
async def create_refresh_token(
    request: RefreshTokenRequestDTO,
    token_service: TokenServiceDependency
):
    token = token_service.create_refresh_token(request)
    return {
        "message": "RefreshToken created successfully",
        "access_token": token,
        "token_type": "Bearer"
    }



@router.post("/set-cookie")
async def set_cookie(
    request: SetCookieTokenDTO,
    response: Response,
    token_service: TokenServiceDependency
):
    token_service.set_tokens_in_cookies(
        response=response,
        request=request
    )

    return {
        "message": "Tokens saved in cookies successfully"
    }


@router.delete("/clear-cookie")
async def clear_cookie(
    response: Response,
    token_service: TokenServiceDependency
):
    token_service.clear_tokens_from_cookies(
        response=response
    )

    return {
        "message": "Tokens removed from cookies successfully"
    }

@router.get("/validate-current-token")
async def validate_current_token(
    request: Request,
    token_service: TokenServiceDependency
):
    access_token = request.cookies.get("access_token")

    if access_token is None:
        return {
            "is_valid": False,
            "error": "token_not_found",
            "message": "Access token was not found in cookies",
            "payload": None
        }

    return token_service.validate_token(access_token)


@router.get("/get-token-info")
async def get_current_user_id(
    request: Request,
    token_service: TokenServiceDependency
) -> int:

    access_token = request.cookies.get("access_token")

    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not found"
        )

    try:
        payload = token_service.decode_token(access_token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )

    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User id not found in token"
        )

    return int(user_id)