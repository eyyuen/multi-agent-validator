import pandas as pd
from core.models import AgentResult, DataProfile


def ingestion_agent(file_path: str) -> AgentResult:
    logs = []
    errors = []

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")

        logs.append(f"Loaded file: {file_path}")
        logs.append(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        date_columns = [col for col in df.columns if "date" in col.lower()]
        logs.append(f"Numeric columns: {numeric_columns}")
        logs.append(f"Date columns: {date_columns}")

        null_counts = df.isnull().sum().to_dict()
        total_nulls = sum(null_counts.values())
        logs.append(f"Total null values found: {total_nulls}")

        if "invoice_id" in df.columns:
            duplicate_ids = df[
                df.duplicated(subset=["invoice_id"], keep=False)
            ]["invoice_id"].unique().tolist()
            logs.append(f"Duplicate invoice IDs found: {len(duplicate_ids)}")
        else:
            duplicate_ids = []

        profile = DataProfile(
            total_rows=df.shape[0],
            total_columns=df.shape[1],
            column_names=df.columns.tolist(),
            null_counts={k: int(v) for k, v in null_counts.items()},
            duplicate_ids=duplicate_ids,
            numeric_columns=numeric_columns,
            date_columns=date_columns
        )

        return AgentResult(
            agent_name="IngestionAgent",
            status="success",
            data={"dataframe": df, "profile": profile},
            logs=logs,
            errors=errors
        )

    except Exception as e:
        errors.append(str(e))
        return AgentResult(
            agent_name="IngestionAgent",
            status="error",
            data={},
            logs=logs,
            errors=errors
        )
