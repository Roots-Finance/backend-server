import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    oauth_sub = Column(String(250), nullable=False, unique=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    nessie_customer_id = Column(String(250), nullable=True)
    plaid_access_token = Column(String(250), nullable=True)
    knot_access_token = Column(String(250), nullable=True)
    budget_configuration = Column(JSONB, nullable=True)

    accounts = relationship("Account", back_populates="user")

    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
