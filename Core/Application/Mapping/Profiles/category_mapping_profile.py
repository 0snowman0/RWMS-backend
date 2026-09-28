from Core.Application.DTOs.Categories.category import (
    CategoryDto,
    CategorySummaryDto,
)
from Core.Application.Mapping.mapper import (
    Mapper,
)
from Core.Application.Mapping.mapping_profile import (
    MappingProfile,
)
from Core.Domain.Models.Categories.category import (
    Category,
)


class CategoryMappingProfile(
    MappingProfile,
):

    def configure(
        self,
        mapper: Mapper,
    ) -> None:

        mapper.create_map(
            Category,
            CategoryDto,
        )

        mapper.create_map(
            Category,
            CategorySummaryDto,
        )
