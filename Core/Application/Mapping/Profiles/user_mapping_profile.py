from Core.Application.DTOs.Users.Commands.user_test import UserCustomDto
from Core.Application.Mapping.mapper import Mapper
from Core.Application.Mapping.mapping_profile import MappingProfile
from Core.Domain.Models.user import User


class UserMappingProfile(MappingProfile):

    def configure(
        self,
        mapper: Mapper,
    ) -> None:

        mapper.create_map(
            UserCustomDto,
            User,
        ).for_member(
            "full_name",
            source="name",
        ).for_member(
            "is_active",
            source="status",
            transform=lambda value: (
                value.lower() == "active"
            ),
        )