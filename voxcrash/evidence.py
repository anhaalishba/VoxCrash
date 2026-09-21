import json
import os
import uuid
from datetime import datetime, timezone

EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "evidence")


def capture(strategy_name: str, violation, state) -> str:
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    fail_id = f"VOICE-FAIL-{uuid.uuid4().hex[:8].upper()}"
    record = {
        "fail_id": fail_id,
        "invariant_id": violation.invariant_id,
        "severity": violation.severity,
        "description": violation.description,
        "attack_strategy": strategy_name,
        "detected_at": datetime.fromtimestamp(violation.detected_at, tz=timezone.utc).isoformat(),
        "tool_call_args": violation.tool_call_args,
        "state_snapshot": violation.state_snapshot,
        "transcript_window": state.recent_transcript_window(seconds=15.0, now=violation.detected_at),
    }
    path = os.path.join(EVIDENCE_DIR, f"{fail_id}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    return path


def print_report_card(violation, strategy_name: str):
    print()
    print("=" * 60)
    print(f"🔴 FAILURE DISCOVERED — {violation.invariant_id}")
    print("=" * 60)
    print(f"Severity:        {violation.severity.upper()}")
    print(f"Attack strategy: {strategy_name}")
    print(f"Description:     {violation.description}")
    print(f"Tool call args:  {violation.tool_call_args}")
    print(f"State snapshot:  {violation.state_snapshot}")
    print("=" * 60)
    print()


def list_evidence() -> list[dict]:
    if not os.path.isdir(EVIDENCE_DIR):
        return []
    records = []
    for fname in sorted(os.listdir(EVIDENCE_DIR)):
        if fname.endswith(".json"):
            with open(os.path.join(EVIDENCE_DIR, fname)) as f:
                records.append(json.load(f))
    return records
