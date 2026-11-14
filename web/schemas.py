"""Pydantic models for request validation and response documentation."""
from typing import Optional

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    customer_tenure_months: float = Field(ge=0, le=600)
    earlier_ticket_count_90d: float = Field(ge=0, le=200)
    sla_consumed_ratio: float = Field(ge=0, le=5)
    account_value_inr_thousands: float = Field(ge=0, le=10000)
    satisfaction_score: float = Field(ge=0, le=100)
    reopened_flag: int = Field(ge=0, le=1)
    self_service_first_flag: int = Field(ge=0, le=1)
    tau: float = Field(default=0.15, ge=0, le=1)
    cost_fp: float = Field(default=50, ge=0, le=100000)
    cost_fn: float = Field(default=400, ge=0, le=100000)


class Contribution(BaseModel):
    feature: str
    value: float
    z: float
    weight: float
    effect: float


class ScoreResponse(BaseModel):
    probability: float
    flagged: bool
    tau: float
    bias: float
    contributions: list[Contribution]
    expected_cost_flag: float
    expected_cost_skip: float


class Confusion(BaseModel):
    tp: int
    fp: int
    tn: int
    fn: int
    accuracy: float
    precision: float
    recall: float
    f1: float
    specificity: float
    fpr: float
    tpr: float


class ThresholdResponse(Confusion):
    dataset: str
    tau: float
    cost_fp: float
    cost_fn: float
    cost: float
    cost_flag_nobody: float
    cost_at_0_5: float
    n: int
    positives: int
