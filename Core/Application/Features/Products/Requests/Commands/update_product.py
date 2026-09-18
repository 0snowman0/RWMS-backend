from dataclasses import dataclass

from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Contracts.Mediators.mediator import (
    IRequest,
)

from Core.Application.DTOs.Products.product import (
    UpdateProductDto,
)

from Core.Application.Mediators.decorators import request_type
from Core.Domain.Enums.Mediators.mediator import (
    RequestType,
)

from Core.Domain.Models.Products.product import (
    Product,
)


@request_type(
    RequestType.COMMAND
)
@dataclass(
    frozen=True,
    slots=True,
)
class UpdateProductCommand(
    IRequest[
        BaseResponse[Product]
    ]
):

    product_id: int

    data: UpdateProductDto