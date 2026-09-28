from sqlalchemy.ext.asyncio import AsyncSession

from Core.Application.Contracts.DataBases.Repositories.AuditLogs.audit_log_repository import (
    IAuditLogRepository,
)
from Core.Application.Contracts.DataBases.Repositories.Categories.category_repository import ICategoryRepository
from Core.Application.Contracts.DataBases.Repositories.Products.product_repository import IProductRepository
from Core.Application.Contracts.DataBases.Repositories.WaybillTemplates.waybill_template_repository import (
    IWaybillTemplateRepository,
)
from Core.Application.Contracts.DataBases.Repositories.Waybills.waybill_repository import (
    IWaybillRepository,
)
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)
from Core.Application.Contracts.DataBases.Repositories.Users.user_repository import (
    IUserRepository,
)

from Infrastructure.Persistence.Repositories.AuditLogs.audit_log_repository import (
    AuditLogRepository,
)
from Infrastructure.Persistence.Repositories.Categories.category_repository import CategoryRepository
from Infrastructure.Persistence.Repositories.Products.product_repository import ProductRepository
from Infrastructure.Persistence.Repositories.WaybillTemplates.waybill_template_repository import (
    WaybillTemplateRepository,
)
from Infrastructure.Persistence.Repositories.Waybills.waybill_repository import (
    WaybillRepository,
)
from Infrastructure.Persistence.Repositories.Users.user_repository import (
    UserRepository,
)


class SqlAlchemyUnitOfWork(IUnitOfWork):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._users = UserRepository(
            session=session,
        )

        self._categories = CategoryRepository(
            session=session,
        )

        self._waybill_templates = WaybillTemplateRepository(
            session=session,
        )
        
        self._waybills = WaybillRepository(
            session=session,
        )

        self._products = ProductRepository(
            session=session,
        )

        self._audit_logs = AuditLogRepository(
            session=session,
        )
        
    @property
    def users(self) -> IUserRepository:
        return self._users
    
    @property
    def categories(
        self,
    ) -> ICategoryRepository:
        return self._categories

    @property
    def products(
        self,
    ) -> IProductRepository:
        return self._products

    @property
    def waybill_templates(
        self,
    ) -> IWaybillTemplateRepository:

        return self._waybill_templates

    @property
    def waybills(
        self,
    ) -> IWaybillRepository:

        return self._waybills

    @property
    def audit_logs(
        self,
    ) -> IAuditLogRepository:
        return self._audit_logs
    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def save_changes(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()