import enum
import uuid

from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from database.db import Base


class MarketCapPreferences(enum.Enum):
    SMALL_CAP = "small_cap"
    MID_CAP = "mid_cap"
    LARGE_CAP = "large_cap"
    MIXED = "mixed"


class GrowthVsValue(enum.Enum):
    GROWTH = "growth"
    VALUE = "value"
    BLEND = "blend"


class CyclicalVsDefensive(enum.Enum):
    CYCLICAL = "cyclical"
    DEFENSIVE = "defensive"
    MIXED = "mixed"


class ValuationMetricsPreference(enum.Enum):
    PE_RATIO = "P/E Ratio"
    PB_RATIO = "P/B Ratio"
    PS_RATIO = "P/S Ratio"
    EV_EBITDA = "EV/EBITDA"
    DIVIDEND_YIELD = "Dividend Yield"
    ROE = "ROE"
    ROA = "ROA"
    PROFIT_MARGIN = "Profit Margin"


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
    is_experienced_investor = Column(Boolean, nullable=True)
    preferred_sectors = Column(String(250), nullable=True)
    sector_preference_rankings = Column(String(250), nullable=True)
    market_cap_preference = Column(String(250), nullable=True)
    growth_vs_value = Column(String(250), nullable=True)
    cyclical_vs_defensive = Column(String(250), nullable=True)
    valuation_metrics_preference = Column(String(250), nullable=True)

    dividend_preference = Column(Boolean, nullable=True)
    tech_sector_interest = Column(Boolean, nullable=True)
    healthcare_sector_interest = Column(Boolean, nullable=True)
    financial_sector_interest = Column(Boolean, nullable=True)
    energy_sector_interest = Column(Boolean, nullable=True)
    consumer_goods_sector_interest = Column(Boolean, nullable=True)
    industrials_sector_interest = Column(Boolean, nullable=True)
    emerging_markets_interest = Column(Boolean, nullable=True)
    esg_preference = Column(Boolean, nullable=True)
    small_cap_interest = Column(Boolean, nullable=True)
    blue_chip_interest = Column(Boolean, nullable=True)
    tech_subsectors_interest = Column(String(500), nullable=True)
    healthcare_subsectors_interest = Column(String(500), nullable=True)
    investment_time_horizon = Column(Integer, nullable=True)
    has_trade_history = Column(Boolean, nullable=True)

    accounts = relationship("Account", back_populates="user")

    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
