# Api/Controllers/Identity/Auth/V1/Authenticates.py
from fastapi import APIRouter, Depends
from Core.Application.DTOs.Identities.Commands.token import TokenRequestDTO
from Core.Application.Contracts.Identities.identity import ITokenService
from Configs.dependencies import get_token_service  

router = APIRouter(tags=["Authenticates"])

@router.post("/create-token")
async def create_token(
    request: TokenRequestDTO,
    token_service: ITokenService = Depends(get_token_service)  
):
    token = token_service.create_access_token(request)
    return {
        "message": "Token created successfully",
        "access_token": token,
        "token_type": "Bearer"
    }