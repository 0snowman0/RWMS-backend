from Core.Application.DTOs.AuditLogs.audit_log import AuditLogDto
from Core.Application.Mapping.mapper import Mapper
from Core.Application.Mapping.mapping_profile import MappingProfile
from Core.Domain.Models.AuditLogs.audit_log import AuditLog


class AuditLogMappingProfile(MappingProfile):

    def configure(
        self,
        mapper: Mapper,
    ) -> None:

        mapper.create_map(
            AuditLog,
            AuditLogDto,
        )
