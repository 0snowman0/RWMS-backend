from Core.Application.Contracts.DataBases.Repositories.Waybills.waybill_repository import (
    IWaybillRepository,
)
from Core.Domain.Models.Waybills.waybill import (
    Waybill,
)
from Infrastructure.Persistence.Repositories.Generics.generic_repository import (
    GenericRepository,
)


class WaybillRepository(
    GenericRepository[Waybill],
    IWaybillRepository,
):

    def __init__(
        self,
        session,
    ) -> None:

        super().__init__(
            session=session,
            entity_type=Waybill,
        )

    async def get_by_waybill_number(
        self,
        waybill_number: str,
    ) -> Waybill | None:

        return await self.get(
            Waybill.waybill_number == waybill_number
        )
