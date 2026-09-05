from Core.Application.Mapping.mapper import Mapper
from Core.Application.Mapping.mapping_profile import MappingProfile
from Core.Application.Mapping.Profiles.user_mapping_profile import (
    UserMappingProfile,
)


def configure_mapper() -> Mapper:

    mapper = Mapper()

    profiles: list[MappingProfile] = [
        UserMappingProfile(),
    ]

    for profile in profiles:
        profile.configure(mapper)

    return mapper