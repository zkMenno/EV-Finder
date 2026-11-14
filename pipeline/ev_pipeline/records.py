"""Shared contract between source adapters (T-004) and matching/merge (T-005).

An adapter turns raw source data into SourceRecords: facts that are not yet tied to one of
our variant ids. Matching assigns the subject id and turns each spec into a schema Fact.
Coordinator-owned: change only between waves.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from ev_pipeline.schema_models import ChargeCurve, Confidence, Country, FactField, Source


class SpecValue(BaseModel):
    value: float | str | bool | ChargeCurve
    unit: str


class SourceRecord(BaseModel):
    source: Source
    record_key: str = Field(description="Stable key of the raw record, e.g. a file path or row id.")
    kind: Literal["spec", "registration_count"] = "spec"
    make: str
    model: str
    variant_name: str | None = None
    year: int | None = Field(default=None, description="Model year (spec) or registration year.")
    country: Country | None = None
    body: str | None = None
    drivetrain: Literal["fwd", "rwd", "awd"] | None = None
    specs: dict[FactField, SpecValue] = Field(default_factory=dict)
    retrieved_at: date
    confidence: Confidence
