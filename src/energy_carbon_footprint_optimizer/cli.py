import argparse
import json
import sys
from .harness import run_harness
from .models import EvaluationReport, ScoringInput


def main():
    parser = argparse.ArgumentParser(
        prog="eco-optimizer",
        description="Energy / Carbon Footprint Optimizer harness CLI",
    )
    parser.add_argument("--input", "-i", required=True, help="JSON file containing a ScoringInput")
    parser.add_argument("--output", "-o", help="JSON file to write (default: stdout)")
    parser.add_argument(
        "--mode",
        default="full",
        choices=["full", "roadmap_only"],
        help="full report or roadmap-only output",
    )
    args = parser.parse_args()

    try:
        with open(args.input, encoding="utf-8-sig") as fh:
            data = json.load(fh)
        scoring_input = ScoringInput.model_validate(data)
    except FileNotFoundError:
        print(f"Input file not found: {args.input}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:
        print(f"Invalid scoring input: {exc}", file=sys.stderr)
        sys.exit(2)

    result = run_harness(scoring_input, mode=args.mode)

    if isinstance(result, EvaluationReport):
        output = result.model_dump_json(indent=2)
    else:
        output = json.dumps([r.model_dump(mode="json") for r in result], indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
