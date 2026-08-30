from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from Infrastructure.Persistence.Configs.PGdatabase import Base


class Role(Base):
    role_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )