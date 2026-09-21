import asyncio
import sys

from voxcrash.bridge import run_attack
from voxcrash.strategies import ALL_STRATEGIES
from voxcrash import evidence


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    command = sys.argv[1]

    if command == "run":
        if len(sys.argv) < 3:
            sys.exit(1)
        target = sys.argv[2]
        strategies = list(ALL_STRATEGIES) if target == "all" else [target]
        for name in strategies:
            if name not in ALL_STRATEGIES:
                sys.exit(1)
            print(f"\n>>> Running attack: {name}\n")
            try:
                asyncio.run(run_attack(name))
            except RuntimeError as e:
                print(f"ERROR: {e}")
                sys.exit(1)

    elif command == "report":
        records = evidence.list_evidence()
        if not records:
            print("No failures captured yet.")
        for r in records:
            print(f"{r['fail_id']}  [{r['severity']}]  {r['invariant_id']}  ({r['attack_strategy']})")
            print(f"  {r['description']}\n")

    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
