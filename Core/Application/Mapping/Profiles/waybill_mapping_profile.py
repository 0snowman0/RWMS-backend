from Core.Application.DTOs.Waybills.waybill import (
    CreateWaybillDto,
    UpdateWaybillDto,
    WaybillDto,
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
            CreateWaybillDto,
            Waybill,
        ).ignore("attributes")

        mapper.create_map(
            UpdateWaybillDto,
            Waybill,
        ).ignore("attributes")
