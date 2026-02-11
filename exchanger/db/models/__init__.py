# Import models so Base.metadata is populated for Alembic autogenerate
from .currency.currency import Currency

__all__ = [
    Currency,
]  # type: ignore
