from pydantic import BaseModel
from typing import Optional, List, Any


class AgentResult(BaseModel):
    agent_name: str
    status: str
    data: Any
    logs: List[str] = []
    errors: List[str] = []


class DataProfile(BaseModel):
    total_rows: int
    total_columns: int
    column_names: List[str]
    null_counts: dict
    duplicate_ids: List[str]
    numeric_columns: List[str]
    date_columns: List[str]


class RuleViolation(BaseModel):
    row_index: int
    invoice_id: str
    field: str
    issue: str
    severity: str


class AIAnomaly(BaseModel):
    row_index: int
    invoice_id: str
    anomaly_type: str
    description: str
    severity: str


class ValidationSummary(BaseModel):
    run_timestamp: str
    total_records: int
    total_violations: int
    total_anomalies: int
    critical_count: int
    warning_count: int
    rule_violations: List[RuleViolation]
    ai_anomalies: List[AIAnomaly]
    data_profile: DataProfile
