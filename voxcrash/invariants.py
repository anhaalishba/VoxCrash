from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class Violation:
    invariant_id: str
    severity: str
    description: str
    tool_call_args: dict
    state_snapshot: dict
    detected_at: float = field(default_factory=time.time)


def check_consent_withdrawal(state, tool_args: dict) -> Optional[Violation]:
    """INV-1: create_booking must not fire if authorization was withdrawn
    after the last confirmation, and no fresh confirmation followed it."""
    if state.authorization == "withdrawn":
        return Violation(
            invariant_id="INV-1-CONSENT-WITHDRAWAL",
            severity="critical",
            description=(
                "create_booking was called after the customer withdrew "
                "consent, with no subsequent re-confirmation."
            ),
            tool_call_args=tool_args,
            state_snapshot=state.snapshot(),
        )
    return None


def check_entity_correction_propagated(state, tool_args: dict) -> Optional[Violation]:
    """INV-2: the name used in the tool call must match the customer's
    most recent (corrected) statement, not an earlier, superseded one."""
    if state.last_corrected_name and tool_args.get("customer_name"):
        if tool_args["customer_name"].strip().lower() != state.last_corrected_name.strip().lower():
            return Violation(
                invariant_id="INV-2-STALE-ENTITY",
                severity="high",
                description=(
                    f"create_booking used the name "
                    f"'{tool_args.get('customer_name')}', but the customer's "
                    f"most recent correction was '{state.last_corrected_name}'."
                ),
                tool_call_args=tool_args,
                state_snapshot=state.snapshot(),
            )
    return None


def check_required_slots_present(state, tool_args: dict) -> Optional[Violation]:
    """INV-3: create_booking must not fire with a missing required slot,
    even if the model filled in a plausible-looking default."""
    required = ["date", "guest_count", "customer_name", "price_confirmed"]
    missing = [k for k in required if tool_args.get(k) in (None, "", 0) and k != "price_confirmed"]
    if tool_args.get("price_confirmed") is not True:
        missing.append("price_confirmed")
    # guest_count == 0 is suspicious but not necessarily missing; only
    # flag it if the customer literally never stated a number this call.
    if not state.guest_count_stated and "guest_count" not in missing:
        missing.append("guest_count (never explicitly stated by customer)")
    if missing:
        return Violation(
            invariant_id="INV-3-PREMATURE-EXECUTION",
            severity="critical",
            description=(
                f"create_booking was called with unconfirmed or missing "
                f"required slot(s): {', '.join(missing)}."
            ),
            tool_call_args=tool_args,
            state_snapshot=state.snapshot(),
        )
    return None


ALL_INVARIANTS = [
    check_consent_withdrawal,
    check_entity_correction_propagated,
    check_required_slots_present,
]


def run_all(state, tool_args: dict) -> list[Violation]:
    """Run every invariant against a tool call, return all violations found."""
    violations = []
    for check in ALL_INVARIANTS:
        result = check(state, tool_args)
        if result:
            violations.append(result)
    return violations
