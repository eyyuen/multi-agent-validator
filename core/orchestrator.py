import traceback
from datetime import datetime
from core.models import ValidationSummary
from agents.ingestion_agent import ingestion_agent
from agents.validation_agent import validation_agent
from agents.anomaly_agent import anomaly_agent
from agents.report_agent import report_agent


class Orchestrator:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.run_log = []

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.run_log.append(entry)
        print(entry)

    def run(self) -> ValidationSummary:
        self.log("🚀 Starting Multi-Agent Validation System")
        self.log(f"📂 Input file: {self.file_path}")

        self.log("\n--- Agent 1: Data Ingestion & Profiling ---")
        try:
            result_1 = ingestion_agent(self.file_path)
            if result_1.status == "error":
                raise Exception(f"Agent 1 failed: {result_1.errors}")
            df = result_1.data["dataframe"]
            profile = result_1.data["profile"]
            for log in result_1.logs:
                self.log(f"  {log}")
            self.log("✅ Agent 1 complete")
        except Exception as e:
            self.log(f"❌ Agent 1 error: {e}")
            raise

        self.log("\n--- Agent 2: Rule-Based Validation ---")
        try:
            result_2 = validation_agent(df, profile)
            if result_2.status == "error":
                raise Exception(f"Agent 2 failed: {result_2.errors}")
            violations = result_2.data["violations"]
            for log in result_2.logs:
                self.log(f"  {log}")
            self.log(f"✅ Agent 2 complete — {len(violations)} violations found")
        except Exception as e:
            self.log(f"❌ Agent 2 error: {e}")
            raise

        self.log("\n--- Agent 3: AI Anomaly Detection ---")
        try:
            result_3 = anomaly_agent(df)
            if result_3.status == "error":
                raise Exception(f"Agent 3 failed: {result_3.errors}")
            anomalies = result_3.data["anomalies"]
            for log in result_3.logs:
                self.log(f"  {log}")
            self.log(f"✅ Agent 3 complete — {len(anomalies)} anomalies found")
        except Exception as e:
            self.log(f"❌ Agent 3 error: {e}")
            raise

        self.log("\n--- Agent 4: Report Generation ---")
        try:
            summary = ValidationSummary(
                run_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total_records=profile.total_rows,
                total_violations=len(violations),
                total_anomalies=len(anomalies),
                critical_count=sum(
                    1 for v in violations if v.severity == "critical"
                ),
                warning_count=sum(
                    1 for v in violations if v.severity == "warning"
                ),
                rule_violations=violations,
                ai_anomalies=anomalies,
                data_profile=profile
            )
            result_4 = report_agent(summary, df)
            for log in result_4.logs:
                self.log(f"  {log}")
            self.log("✅ Agent 4 complete")
        except Exception as e:
            self.log(f"❌ Agent 4 error: {e}")
            raise

        self.log("\n🎉 Validation pipeline complete!")
        self.log(f"📊 Total records: {summary.total_records}")
        self.log(f"🚨 Rule violations: {summary.total_violations}")
        self.log(f"🤖 AI anomalies: {summary.total_anomalies}")

        return summary
