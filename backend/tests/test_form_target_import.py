"""Tests for importing generated form targets. Run from backend/:

    python -m unittest tests.test_form_target_import
"""

import unittest
from uuid import uuid4

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session

from app.models.content import (
    Content,
    ContentReport,
    VocabularyExample,
    VocabularyExampleTarget,
    VocabularyForm,
    VocabularyTopic,
)
from app.services.form_target_import import build_rows, headword_target, replace_forms


class HeadwordTargetTest(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(headword_target("talo", "noun", None), ("nominative_singular", "inflected_form"))
        self.assertEqual(headword_target("puhua", "verb", None), ("first_infinitive", "inflected_form"))
        self.assertEqual(headword_target("ei", "verb", "negative_auxiliary"), ("negative_verb_3sg", "inflected_form"))
        self.assertEqual(headword_target("ja", "conjunction", None), ("invariant", "invariant"))
        self.assertEqual(headword_target("kanssa", "adposition", "postposition"), ("invariant", "invariant"))
        self.assertEqual(headword_target("koko", "adjective", "determiner_like"), ("invariant", "invariant"))
        self.assertEqual(headword_target("molemmat", "pronoun", None), ("nominative_plural", "inflected_form"))


def sample():
    talo, ja = str(uuid4()), str(uuid4())
    vocabulary = [
        {"id": talo, "word": "talo", "part_of_speech": "noun", "pos_subtype": ""},
        {"id": ja, "word": "ja", "part_of_speech": "conjunction", "pos_subtype": ""},
    ]
    combined = {"prompt_version": "form_generation_v3", "items": [
        {"content_id": talo, "word": "talo", "part_of_speech": "noun", "forms": [
            {"form": "talon", "grammatical_label": "genitive_singular", "target_type": "inflected_form",
             "notes": "", "source": "model"},
            {"form": "taloa", "grammatical_label": "partitive_singular", "target_type": "inflected_form",
             "notes": "", "source": "correction"}]},
        {"content_id": ja, "word": "ja", "part_of_speech": "conjunction", "forms": []},
    ]}
    return vocabulary, combined


class BuildRowsTest(unittest.TestCase):
    def test_headword_first_then_generated(self):
        vocabulary, combined = sample()
        rows = build_rows(combined, vocabulary, "gpt-test")
        self.assertEqual([(r["form"], r["grammatical_label"], r["display_order"]) for r in rows], [
            ("talo", "nominative_singular", 1), ("talon", "genitive_singular", 2), ("taloa", "partitive_singular", 3),
            ("ja", "invariant", 1)])
        self.assertTrue(rows[2]["source_note"].endswith("manual correction"))
        self.assertTrue(all(r["review_status"] == "active" for r in rows))

    def test_missing_item_stops(self):
        vocabulary, combined = sample()
        combined["items"].pop()
        with self.assertRaises(ValueError):
            build_rows(combined, vocabulary, "gpt-test")


class ReplaceFormsTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
        for model in (VocabularyTopic, Content, VocabularyForm, VocabularyExample, VocabularyExampleTarget, ContentReport):
            model.__table__.create(engine)
        self.session = Session(engine)
        self.vocabulary, self.combined = sample()
        topic = VocabularyTopic(id=uuid4(), slug="t", name_en="T", name_fi="T", sort_order=1)
        self.session.add(topic)
        self.session.flush()
        for order, row in enumerate(self.vocabulary, start=1):
            self.session.add(Content(id=__import__("uuid").UUID(row["id"]), content_type="vocabulary_item",
                                     practice_mode="m", practice_method="p", content=row["word"], language_code="fi",
                                     topic_id=topic.id, topic_order=order, status="active"))
        self.session.flush()
        talo_id = __import__("uuid").UUID(self.vocabulary[0]["id"])
        old = VocabularyForm(id=uuid4(), content_id=talo_id, form="talo", grammatical_label="N sg",
                             target_type="inflected_form", display_order=1, review_status="reviewed", source_note="v0")
        example = VocabularyExample(id=uuid4(), content_id=talo_id, finnish_sentence="Talo on iso.",
                                    written_finnish_sentence="Talo on iso.", normalized_sentence="talo on iso",
                                    english_translation="The house is big.", difficulty="A1",
                                    validation_status="auto_valid", generation_model="t", prompt_version="t")
        for row in (old, example):
            self.session.add(row)
            self.session.flush()
        self.session.add(VocabularyExampleTarget(example_id=example.id, vocabulary_form_id=old.id, role="primary",
                                                 target_validation_status="auto_valid"))
        self.session.commit()

    def count(self, model):
        return self.session.scalar(select(func.count()).select_from(model))

    def test_dry_run_changes_nothing(self):
        counts = replace_forms(self.session, build_rows(self.combined, self.vocabulary, "m"), apply=False)
        self.assertEqual((counts.old_forms, counts.old_examples, counts.new_forms), (1, 1, 4))
        self.assertEqual(self.count(VocabularyForm), 1)

    def test_apply_replaces_forms_and_old_examples(self):
        replace_forms(self.session, build_rows(self.combined, self.vocabulary, "m"), apply=True)
        self.session.commit()
        self.assertEqual((self.count(VocabularyForm), self.count(VocabularyExample),
                          self.count(VocabularyExampleTarget)), (4, 0, 0))
        statuses = set(self.session.scalars(select(VocabularyForm.review_status)))
        self.assertEqual(statuses, {"active"})


if __name__ == "__main__":
    unittest.main()
