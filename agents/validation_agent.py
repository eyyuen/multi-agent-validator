import pandas as pd
from core.models import AgentResult, DataProfile, RuleViolation


def validation_agent(df: pd.DataFrame, profile: DataProfile) -> AgentResult:
    logs = []
    errors = []
    violations = []

    try:
        VALID_STATUSES = ["Pending", "Approved", "Rejected", "Paid"]
        VALID_CURRENCIES = ["SGD", "USD", "EUR", "GBP", "JPY"]
        KNOWN_APPROVERS = ["alice.tan", "bob.lim", "carol.ng", "david.koh"]

        df["amount"] = df["amount"].round(2)

        for idx, row in df.iterrows():
            inv_id = str(row.get("invoice_id", f"ROW-{idx}"))

            if inv_id in profile.duplicate_ids:
                violations.append(RuleViolation(
                    row_index=idx, invoice_id=inv_id, field="invoice_id",
                    issue=f"Duplicate invoice ID: {inv_id}", severity="critical"
                ))

            if pd.isnull(row.get("vendor_name")):
                violations.append(RuleViolation(
                    row_index=idx, invoice_id=inv_id, field="vendor_name",
                    issue="Vendor name is missing", severity="critical"
                ))

            amount = row.get("amount")
            if pd.notnull(amount) and amount <= 0:
                violations.append(RuleViolation(
                    row_index=idx, invoice_id=inv_id, field="amount",
                    issue=f"Invalid amount: {amount}", severity="critical"
                ))

            try:
                invoice_date = pd.to_datetime(row.get("invoice_date"))
                due_date = pd.to_datetime(row.get("due_date"))
                if pd.notnull(invoice_date) and pd.notnull(due_date):
                    if due_date < invoice_date:
                        violations.append(RuleViolation(
                            row_index=idx, invoice_id=inv_id, field="due_date",
                            issue=(
                                f"Due date {due_date.date()} is before "
                                f"invoice date {invoice_date.date()}"
                            ),
                            severity="critical"
                        ))
            except Exception:
                violations.append(RuleViolation(
                    row_index=idx, invoice_id=inv_id,
                    field="invoice_date/due_date",
                    issue="Could not parse date values", severity="warning"
                ))

            status = row.get("status")
            if pd.notnull(status) and status not in VALID_STATUSES:
                violations.append(RuleViolation(
                    row_index=idx, invoice_id=inv_id, field="status",
                    issue=f"Invalid status value: '{status}'",
                    severity="warning"
                ))

            currency = row.get("currency")
            if pd.notnull(currency) and currency not in VALID_CURRENCIES:
                violations.append(RuleViolation(
                    row_index=idx, invoice_id=inv_id, field="currency",
                    issue=f"Invalid currency code: '{currency}'",
                    severity="warning"
                ))

            approver = row.get("approved_by")
            if pd.notnull(approver) and approver not in KNOWN_APPROVERS:
                violations.append(RuleViolation(
                    row_index=idx, invoice_id=inv_id, field="approved_by",
                    issue=f"Unknown approver: '{approver}'",
                    severity="warning"
                ))

        critical = sum(1 for v in violations if v.severity == "critical")
        warning = sum(1 for v in violations if v.severity == "warning")
        logs.append(f"Checked {len(df)} records against 7 rules")
        logs.append(f"Critical violations: {critical}")
        logs.append(f"Warning violations: {warning}")

        return AgentResult(
            agent_name="ValidationAgent",
            status="success",
            data={"violations": violations},
            logs=logs,
            errors=errors
        )

    except Exception as e:
        errors.append(str(e))
        return AgentResult(
            agent_name="ValidationAgent",
            status="error",
            data={"violations": []},
            logs=logs,
            errors=errors
        )
