"""Replace the form targets in the database with a generated set (default: v3_all).

Adds one headword target per word, deletes the old (v0) form targets and the old
example sentences linked to them, and inserts the new targets, in one transaction.
Without --apply it only checks the data and the database and prints what would change.

Back up first, into its own directory so a later export does not overwrite it:
                python -m scripts.export_database --output data-generation/exports/backup-YYYY-MM-DD
Then:           python -m scripts.import_form_targets            # dry run
                python -m scripts.import_form_targets --apply    # write
"""

import argparse
import json
import sys
from collections import Counter

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import create_database_engine
from app.services.form_target_generator import OUTPUTS_DIR, VOCABULARY_CSV, load_vocabulary, output_dir_for
from app.services.form_target_import import REQUIRED_MIGRATION, build_rows, replace_forms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--set", default="all", dest="set_name", help="Generated set to import (default: all)")
    parser.add_argument("--apply", action="store_true", help="Write to the database (default: dry run)")
    args = parser.parse_args()

    out = output_dir_for(args.set_name, OUTPUTS_DIR)
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    unfinished = [b["batch_id"] for b in manifest["batches"] if b["status"] != "done"]
    if unfinished:
        sys.exit(f"Stopped: {len(unfinished)} batches are not done in {out.name}.")
    combined = json.loads((out / "combined.json").read_text(encoding="utf-8"))
    try:
        rows = build_rows(combined, load_vocabulary(VOCABULARY_CSV), manifest["model"])
    except ValueError as error:
        sys.exit(f"Stopped: {error}")

    engine = create_database_engine()
    try:
        with Session(engine) as session:
            with session.begin():
                version = session.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                if version != REQUIRED_MIGRATION:
                    sys.exit(f"Stopped: database is at migration {version}; run `alembic upgrade head` first.")
                try:
                    counts = replace_forms(session, rows, apply=args.apply)
                except ValueError as error:
                    sys.exit(f"Stopped: {error}")
                if not args.apply:
                    session.rollback()
    finally:
        engine.dispose()

    types = Counter(row["target_type"] for row in rows)
    print(f"Source: {out.name}/combined.json ({combined['prompt_version']}, {manifest['model']})")
    print(f"Vocabulary items: {counts.vocabulary_items}")
    print(f"Delete: {counts.old_forms} form targets, {counts.old_example_links} example links, "
          f"{counts.old_examples} examples")
    print(f"Insert: {counts.new_forms} form targets " + str(dict(types)))
    print("Done: changes committed." if args.apply else "Dry run: nothing was written. Add --apply to import.")


if __name__ == "__main__":
    main()
