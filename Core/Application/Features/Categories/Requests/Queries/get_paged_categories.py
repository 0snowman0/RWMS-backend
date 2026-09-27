from dataclasses import dataclass

from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequest,
)
from Core.Application.DTOs.Categories.category import (
    CategorySummaryDto,
)
from Core.Application.DTOs.Common.pagination_dto import (
    PagedRequestDto,
    PagedResultDto,
)
from Core.Application.Mediators.decorators import (
    request_type,
)
from Core.Domain.Enums.Mediators.mediator import (
    RequestType,
)


@request_type(
    RequestType.QUERY
)
@dataclass(
    frozen=True,
    slots=True,
)
class GetPagedCategoriesQuery(
    IRequest[
        BaseResponse[PagedResultDto[CategorySummaryDto]]
    ]
):

    pagination: PagedRequestDto[None]
