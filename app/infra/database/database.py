from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    id: Any
    __name__: str

    __allow_unmapped__ = True
