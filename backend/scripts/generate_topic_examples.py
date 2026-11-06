"""Generate and save missing Finnish example sentences for one topic."""

import argparse
from dataclasses import asdict

from sqlalchemy.orm import sessionmaker

from app.database import create_database_engine
from app.services.content_generator import generate_missing_topic_examples
from app.services.content_readiness import calculate_topic_readiness


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True, help="Topic slug, for example pronouns-and-reference")
    parser.add_argument("--limit", type=int, help="Maximum target forms to generate in this run")
    parser.add_argument("--model", default="gpt-6-luna")
    args = parser.parse_args()

    engine = create_database_engine()
    session_factory = sessionmaker(bind=engine)
    try:
        summary = generate_missing_topic_examples(
            session_factory,
            topic_slug=args.topic,
            limit=args.limit,
            model=args.model,
        )
        print("Generation:")
        for key, value in asdict(summary).items():
            print(f"  {key}: {value}")
        with session_factory() as session:
            readiness = calculate_topic_readiness(session, args.topic)
        print("Coverage:")
        print(
            f"  vocabulary: {readiness.vocabulary_items.covered}/"
            f"{readiness.vocabulary_items.total} ({readiness.vocabulary_items.percent}%)"
        )
        for target_type, coverage in readiness.targets_by_type.items():
            print(
                f"  {target_type}: {coverage.covered}/{coverage.total} "
                f"({coverage.percent}%)"
            )
        print(
            f"  all targets: {readiness.total_targets.covered}/"
            f"{readiness.total_targets.total} ({readiness.total_targets.percent}%)"
        )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
