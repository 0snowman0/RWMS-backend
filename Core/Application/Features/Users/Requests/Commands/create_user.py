from dataclasses import dataclass

from Core.Application.Contracts.Mediators.mediator import IRequest
from Core.Application.DTOs.Users.Commands.user_test import (
    UserCustomDto,
)
from Core.Application.Mediators.decorators import request_type
from Core.Domain.Enums.Mediators.mediator import RequestType
from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Domain.Models.user import User


@request_type(RequestType.COMMAND)
@dataclass(frozen=True, slots=True)
class CreateUserCommand(
    IRequest[
        BaseResponse[User]
    ]
):
    data: UserCustomDto