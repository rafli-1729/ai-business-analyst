def collect_evidence(
    findings: list[dict],
) -> dict:

    evidence = {
        "findings": findings,
        "total_tasks": len(findings),
    }

    return evidence