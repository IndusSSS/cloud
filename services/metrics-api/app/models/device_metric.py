from __future__ import annotations

from datetime import datetime
from sqlmodel import Field, SQLModel


class DeviceMetric(SQLModel, table=True):
    __tablename__ = "device_metrics"

    id: int | None = Field(default=None, primary_key=True)
    device_id: str
    ts: datetime
    type: str
    value: float
    unit: str

