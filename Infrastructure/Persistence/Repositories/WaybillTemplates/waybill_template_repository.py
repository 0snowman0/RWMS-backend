from Core.Application.Contracts.DataBases.Repositories.WaybillTemplates.waybill_template_repository import (
    IWaybillTemplateRepository,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)
from Infrastructure.Persistence.Repositories.Generics.generic_repository import (
    GenericRepository,
)


class WaybillTemplateRepository(
    GenericRepository[WaybillTemplate],
    IWaybillTemplateRepository,
):

    def __init__(
        self,
        session,
    ) -> None:

        super().__init__(
            session=session,
            entity_type=WaybillTemplate,
        )

    async def get_by_name(
        self,
        name: str,
    ) -> WaybillTemplate | None:

        return await self.get(
            WaybillTemplate.name == name
        )
