from dataclasses import dataclass

from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequest,
)
from Core.Application.DTOs.WaybillTemplates.waybill_template import (
    WaybillTemplateDto,
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
class GetWaybillTemplateByIdQuery(
    IRequest[
        BaseResponse[WaybillTemplateDto]
    ]
):

    template_id: int
