# flake8: noqa
from datetime import date
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Date
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Corporate(Base):
    __tablename__ = "corporate"
    id: Mapped[int] = mapped_column(primary_key=True)
    jcn: Mapped[str] = mapped_column(String(255), unique=True)
    name_jp: Mapped[str] = mapped_column(String(255))
    name_eng: Optional[Mapped[str]] = mapped_column(String(255), nullable=True)
    sec_code: Optional[Mapped[str]] = mapped_column(String(255), unique=True, nullable=True)  # noqa: E501
    edinet_code: Mapped[str] = mapped_column(String(255), unique=True)
    filing_date_of_ref_doc: Mapped[date] = mapped_column(Date)
    updated_at: Mapped[date] = mapped_column(Date)
