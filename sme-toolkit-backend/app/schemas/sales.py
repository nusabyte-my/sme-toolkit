from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

SalesStatus = Literal['pending', 'completed', 'refunded', 'cancelled']


class SalesTransactionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    platform: str = Field(min_length=1, max_length=60, pattern=r'^[a-z0-9_-]+$')
    external_id: str | None = Field(default=None, max_length=120)
    amount: Decimal = Field(gt=0, le=999999999, max_digits=11, decimal_places=2, allow_inf_nan=False)
    currency: str = Field(default='MYR', pattern=r'^[A-Z]{3}$')
    status: SalesStatus = 'completed'
    transaction_date: datetime

    @field_validator('transaction_date')
    @classmethod
    def valid_date(cls, value):
        if value.tzinfo is None:
            raise ValueError('Include the timezone offset in the transaction date')
        if value > datetime.now(timezone.utc):
            raise ValueError('A recorded sale cannot be dated in the future')
        return value.astimezone(timezone.utc).replace(tzinfo=None)


class SalesTransactionUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: SalesStatus
