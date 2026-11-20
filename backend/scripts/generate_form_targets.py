"""Generate Finnish form targets with the current prompt into local files (no database writes).

Run the same command again to resume an interrupted run.
"""

import argparse
import sys

from app.services.form_target_generator import DEFAULT_BATCH_SIZE, DEFAULT_MODEL, StopRun, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--set", required=True, dest="set_name",
                        help="pilot, all, topic:<slug>, or the name of a file in data-generation/form_targets/sets/")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                        help="Maximum words per batch when a topic has more than 20 words")
    parser.add_argument("--retry-failed", action="store_true", help="Also run batches with status 'failed'")
    parser.add_argument("--only", metavar="BATCH_ID", help="Run one batch, whatever its status")
    parser.add_argument("--dry-run", action="store_true", help="Write the plan and inputs without calling the model")
    parser.add_argument("--reuse", metavar="SET",
                        help="Copy accepted batches with the same words from another set (same prompt and model), e.g. pilot")
    args = parser.parse_args()

    try:
        summary = run(
            args.set_name,
            model=args.model,
            batch_size=args.batch_size,
            retry_failed=args.retry_failed,
            only=args.only,
            dry_run=args.dry_run,
            reuse=args.reuse,
        )
    except StopRun as error:
        print(f"Stopped: {error}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted. Progress is saved; run the same command to continue.", file=sys.stderr)
        sys.exit(130)

    print(
        f"Batches: {summary.done} done, {summary.failed} failed, {summary.pending} pending "
        f"(of {summary.planned}; {summary.ran} run now). Warnings: {summary.warnings}."
    )
    if summary.reused:
        print(f"Reused batches: {summary.reused}.")
    print(f"Corrections applied: {summary.corrections_applied}.")
    print(f"Output: {summary.output_dir}")
    if summary.failed:
        print("Retry failed batches with --retry-failed.")


if __name__ == "__main__":
    main()
