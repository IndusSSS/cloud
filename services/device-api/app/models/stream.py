from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StreamPayload(BaseModel):
    ts: datetime = Field(..., description="Timestamp of the sample")
    type: str = Field(..., description="Metric type")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")

