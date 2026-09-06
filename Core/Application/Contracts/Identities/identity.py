from typing import Any, Protocol
from fastapi import Response
from Core.Application.DTOs.Identities.Commands.token import TokenRequestDTO, RefreshTokenRequestDTO, SetCookieTokenDTO


class ITokenService(Protocol):
    
    def create_access_token(self, request: TokenRequestDTO) -> str:
        ...
    
    def create_refresh_token(self, request:RefreshTokenRequestDTO) -> str:
        ...    
    
    def set_tokens_in_cookies(self, RequestViewModel:SetCookieTokenDTO, resonse: Response) -> None:
        ...
        
    def clear_tokens_from_cookies(self, response: Response) -> None:
        ...        

    def decode_token(
        self,
        token: str
    ) -> dict[str, Any]:
        ...        