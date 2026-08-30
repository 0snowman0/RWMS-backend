from typing import Protocol

from Core.Application.DTOs.Identities.Commands.token import TokenRequestDTO


class ITokenService(Protocol):
    
    def create_access_token(self, request: TokenRequestDTO) -> str:
        ...
        
