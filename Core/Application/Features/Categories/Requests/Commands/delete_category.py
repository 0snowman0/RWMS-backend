from dataclasses import dataclass

from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Contracts.Mediators.mediator import (
    IRequest,
)

from Core.Application.Mediators.decorators import request_type
from Core.Domain.Enums.Mediators.mediator import (
    RequestType,
)


@request_type(
    RequestType.COMMAND
)
@dataclass(
    frozen=True,
    slots=True,
)
class DeleteCategoryCommand(
    IRequest[
        BaseResponse[bool]
    ]
):

    category_id: int