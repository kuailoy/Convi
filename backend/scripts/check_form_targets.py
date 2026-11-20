"""Check generated form targets with Voikko (Finnish morphological analyser).

Reads combined.json of a generated set (with corrections applied) and writes
voikko_report.csv next to it. Findings are hints to look at, not certain errors.

    python -m scripts.check_form_targets --set all
"""

import argparse
import csv
import json
import sys
from collections import Counter

from app.services.form_target_generator import OUTPUTS_DIR, output_dir_for
from app.services.voikko_check import VoikkoChecker


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--set", required=True, dest="set_name", help="Set name used for generation, e.g. all or pilot")
    args = parser.parse_args()

    checker = VoikkoChecker.create()
    if checker is None:
        print("Voikko is not installed (see app/services/voikko_check.py for installation).", file=sys.stderr)
        sys.exit(1)
    out = output_dir_for(args.set_name, OUTPUTS_DIR)
    combined = json.loads((out / "combined.json").read_text(encoding="utf-8"))

    rows, total = [], 0
    for item in combined["items"]:
        for target in item["forms"]:
            total += 1
            for code, message in checker.check(item["word"], item["part_of_speech"], target["form"],
                                               target["grammatical_label"], target["target_type"]):
                rows.append({"topic_slug": item["topic_slug"], "word": item["word"],
                             "part_of_speech": item["part_of_speech"], "form": target["form"],
                             "grammatical_label": target["grammatical_label"], "target_type": target["target_type"],
                             "source": target.get("source", ""), "code": code, "message": message})

    report = out / "voikko_report.csv"
    with report.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["topic_slug", "word", "part_of_speech", "form", "grammatical_label",
                                                    "target_type", "source", "code", "message"])
        writer.writeheader()
        writer.writerows(rows)
    counts = Counter(row["code"] for row in rows)
    print(f"Checked {total} targets: {len(rows)} findings " + str(dict(counts)))
    print(f"Report: {report}")


if __name__ == "__main__":
    main()
