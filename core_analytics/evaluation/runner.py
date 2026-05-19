"""
Evaluation runner for analytical queries.
"""

import json
from pathlib import Path

def load_golden_queries() -> list[dict]:
    """Loads golden queries from the evals directory."""
    baseline_path = Path("evals/golden_queries/baseline.json")
    if not baseline_path.exists():
        return []
        
    with open(baseline_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_evaluation() -> dict:
    """Stub for running evaluations against golden queries."""
    queries = load_golden_queries()
    
    results = {
        "total": len(queries),
        "passed": 0,
        "failed": len(queries),
        "details": []
    }
    
    for q in queries:
        # In a real evaluation, we would invoke the orchestrator here
        # and compare the generated SQL with the expected SQL using an LLM as a judge.
        results["details"].append({
            "question": q["question"],
            "status": "UNTESTED"
        })
        
    return results

if __name__ == "__main__":
    print(run_evaluation())
