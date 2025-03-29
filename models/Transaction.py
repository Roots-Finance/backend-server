import enum
import uuid

from sqlalchemy import Column, Date, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.db import Base


class TransactionType(enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    account = relationship("Account", back_populates="transactions")

    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    merchant = relationship("Merchant", back_populates="transactions")
