from Api.Configs.app_router import AppRouter
from Core.Application.DTOs.Categories.category import (
    CreateCategoryDto,
)

from Core.Application.Features.Categories.Requests.Commands.create_category import (
    CreateCategoryCommand,
)

from Configs.dependencies import (
    MediatorDependency,
)

router = AppRouter(
    tags=["category"]
)

