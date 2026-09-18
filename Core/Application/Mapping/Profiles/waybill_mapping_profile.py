from Core.Application.DTOs.Waybills.waybill import (
    WaybillDto,
    WaybillItemDto,
    WaybillSummaryDto,
)
from Core.Application.Mapping.mapper import (
    Mapper,
)
from Core.Application.Mapping.mapping_profile import (
    MappingProfile,
)
from Core.Domain.Models.Waybills.waybill import (
    Waybill,
)
from Core.Domain.Models.Waybills.waybill_item import (
    WaybillItem,
)


class WaybillMappingProfile(
    MappingProfile,
):

    def configure(
        self,
        mapper: Mapper,
    ) -> None:

        mapper.create_map(
            Waybill,
            WaybillDto,
        )

        mapper.create_map(
            Waybill,
            WaybillSummaryDto,
        )

        mapper.create_map(
            WaybillItem,
            WaybillItemDto,
        )
