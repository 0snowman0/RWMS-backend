from typing import Protocol

from Core.Application.Contracts.DataBases.Repositories.Generics.repository import (
    IGenericRepository,
)
from Core.Domain.Models.Waybills.waybill import (
    Waybill,
)


class IWaybillRepository(
    IGenericRepository[Waybill],
    Protocol,
):

    async def get_by_waybill_number(
        self,
        waybill_number: str,
    ) -> Waybill | None:
        ...

    async def get_by_status(
        self,
        status: str,
    ) -> list[Waybill]:
        ...
