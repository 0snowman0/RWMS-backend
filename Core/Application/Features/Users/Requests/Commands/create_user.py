from dataclasses import dataclass

from Core.Application.DTOs.Users.Commands.user_test import (
    UserCustomDto,
)
from Core.Application.Mediators.decorators import request_type
from Core.Domain.Enums.Mediators.mediator import RequestType



@request_type(RequestType.COMMAND)
@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    data: UserCustomDto