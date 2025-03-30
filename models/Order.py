import enum
import uuid

from sqlalchemy import Column, Date, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.db import Base


class OrderType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(OrderType), nullable=False)
    shares = Column(Float, nullable=False)
    price_per_share = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    ticker = Column(String(250), nullable=False)

    portfolio_id = Column(
        UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False
    )
    portfolio = relationship("Portfolio", back_populates="orders")
