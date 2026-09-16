from dataclasses import dataclass

from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Contracts.Mediators.mediator import (
    IRequest,
)

from Core.Application.DTOs.Categories.category import (
    UpdateCategoryDto,
)


from Core.Application.Mediators.decorators import request_type
from Core.Domain.Enums.Mediators.mediator import (
    RequestType,
)

from Core.Domain.Models.Categories.category import (
    Category,
)


@request_type(
    RequestType.COMMAND
)
@dataclass(
    frozen=True,
    slots=True,
)
class UpdateCategoryCommand(
    IRequest[
        BaseResponse[Category]
    ]
):

    category_id: int

    data: UpdateCategoryDto