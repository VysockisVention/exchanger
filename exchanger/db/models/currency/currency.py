from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from exchanger.db.base import Base


class Currency(Base):
    __tablename__ = "currencies"

    currencyshort: Mapped[str] = mapped_column(String(5), primary_key=True)
    currency: Mapped[str] = mapped_column(String(100), nullable=False)
