import os
import sys
from core.orchestrator import Orchestrator


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else "sample_data/invoices_sample.csv"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    os.makedirs("output", exist_ok=True)

    orchestrator = Orchestrator(file_path)
    summary = orchestrator.run()

    print(f"\n📄 Report saved to: output/validation_report.xlsx")


if __name__ == "__main__":
    main()
