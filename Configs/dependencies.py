from Core.Application.Contracts.Identities.identity import ITokenService
from Infrastructure.Identity.Services.Identities.identity import JWTTokenService


def get_token_service() -> ITokenService:
    return JWTTokenService()