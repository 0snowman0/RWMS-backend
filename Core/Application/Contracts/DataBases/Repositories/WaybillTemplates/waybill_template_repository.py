from typing import Protocol

from Core.Application.Contracts.DataBases.Repositories.Generics.repository import (
    IGenericRepository,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)


class IWaybillTemplateRepository(
    IGenericRepository[WaybillTemplate],
    Protocol,
):

    async def get_by_name(
        self,
        name: str,
    ) -> WaybillTemplate | None:
        ...
