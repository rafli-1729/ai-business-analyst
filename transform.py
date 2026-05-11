import os

from dotenv import load_dotenv

from orchestration.warehouse_pipeline import run_warehouse_elt


def main() -> None:
    load_dotenv()

    database_url = os.getenv("DATABASE_URL", "").strip()

    if not database_url:
        raise ValueError("Missing DATABASE_URL")

    result = run_warehouse_elt(database_url)

    print("\nELT completed.")
    print(f"run_id={result['run_id']}")
    print(f"quality_issue_count={result['quality_issue_count']}")
    print("executed_files=" + ", ".join(result["executed_files"]))


if __name__ == "__main__":
    main()
