from Core.Application.DTOs.WaybillTemplates.waybill_template import (
    WaybillTemplateDto,
    WaybillTemplateSummaryDto,
)
from Core.Application.Mapping.mapper import (
    Mapper,
)
from Core.Application.Mapping.mapping_profile import (
    MappingProfile,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)


class WaybillTemplateMappingProfile(
    MappingProfile,
):

    def configure(
        self,
        mapper: Mapper,
    ) -> None:

        mapper.create_map(
            WaybillTemplate,
            WaybillTemplateDto,
        )

        mapper.create_map(
            WaybillTemplate,
            WaybillTemplateSummaryDto,
        )
