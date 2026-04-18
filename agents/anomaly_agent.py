import json
import traceback
import anthropic
import pandas as pd
from core.models import AgentResult, AIAnomaly


def anomaly_agent(df: pd.DataFrame) -> AgentResult:
    logs = []
    errors = []
    anomalies = []

    try:
        client = anthropic.Anthropic()

        vendor_stats = df.groupby("vendor_name")["amount"].agg(
            ["mean", "max", "count"]
        ).round(2).to_dict(orient="index")

        category_stats = df.groupby("category")["amount"].agg(
            ["mean", "max"]
        ).round(2).to_dict(orient="index")

        records = df.to_dict(orient="records")

        prompt = f"""You are a financial data auditor AI.
Analyze the following corporate invoice dataset for anomalies
that rule-based checks would miss.

VENDOR STATISTICS (normal spending patterns):
{json.dumps(vendor_stats, indent=2)}

CATEGORY STATISTICS (normal spending patterns):
{json.dumps(category_stats, indent=2)}

FULL INVOICE RECORDS:
{json.dumps(records, indent=2)}

Identify anomalies such as:
- Amounts unusually high compared to vendor or category averages
- Suspicious vendor names (typos, impersonation of known vendors)
- Category and amount mismatches
- Any other patterns that suggest errors or fraud risk

Return ONLY a JSON array. No explanation, no markdown, no preamble.
Each item must have exactly these fields:
- row_index (integer)
- invoice_id (string)
- anomaly_type (string)
- description (string)
- severity: "high", "medium", or "low"

If no anomalies found, return an empty array: []
"""

        logs.append("Sending data to Claude for anomaly analysis...")

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text
        logs.append("Received response from Claude")

        clean_response = response_text.strip()
        if "```" in clean_response:
            parts = clean_response.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("["):
                    clean_response = part
                    break

        last_bracket = clean_response.rfind("]")
        if last_bracket != -1:
            clean_response = clean_response[:last_bracket + 1]

        anomaly_data = json.loads(clean_response)
        logs.append(f"Claude identified {len(anomaly_data)} anomalies")

        for item in anomaly_data:
            anomalies.append(AIAnomaly(
                row_index=item["row_index"],
                invoice_id=item["invoice_id"],
                anomaly_type=item["anomaly_type"],
                description=item["description"],
                severity=item["severity"]
            ))

        return AgentResult(
            agent_name="AnomalyAgent",
            status="success",
            data={"anomalies": anomalies},
            logs=logs,
            errors=errors
        )

    except Exception as e:
        errors.append(str(e))
        traceback.print_exc()
        return AgentResult(
            agent_name="AnomalyAgent",
            status="error",
            data={"anomalies": []},
            logs=logs,
            errors=errors
        )
