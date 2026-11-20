"""Tests for problem reports from the app. Run from backend/:

    python -m unittest tests.test_content_reports
"""

import unittest
from uuid import uuid4

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.models.content import Content, ContentReport, VocabularyExample, VocabularyForm, VocabularyTopic
from app.services.content_reports import ReportInvalid, ReportNotFound, create_report

TABLES = [m.__table__ for m in (VocabularyTopic, Content, VocabularyForm, VocabularyExample, ContentReport)]


class ContentReportTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
        for table in TABLES:
            table.create(engine)
        self.session = Session(engine)
        topic = VocabularyTopic(id=uuid4(), slug="food-and-drink", name_en="Food and drink", name_fi="Ruoka ja juoma", sort_order=1)
        self.word = Content(id=uuid4(), content_type="vocabulary_item", practice_mode="structured_drill",
                            practice_method="substitution", content="kahvi", language_code="fi",
                            topic_id=topic.id, topic_order=1, status="active")
        self.form = VocabularyForm(id=uuid4(), content_id=self.word.id, form="kahvia", grammatical_label="partitive_singular",
                                   target_type="inflected_form", display_order=1, source_note="test")
        self.example = VocabularyExample(id=uuid4(), content_id=self.word.id, finnish_sentence="Mä juon kahvia.",
                                         written_finnish_sentence="Juon kahvia.", normalized_sentence="mä juon kahvia",
                                         english_translation="I drink coffee.", difficulty="A1", validation_status="auto_valid",
                                         generation_model="test", prompt_version="test")
        for row in (topic, self.word, self.form, self.example):  # parents first
            self.session.add(row)
            self.session.flush()
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_new_forms_default_to_active(self):
        self.assertEqual(self.form.review_status, "active")

    def test_sentence_report_flags_example(self):
        report = create_report(self.session, content_id=self.word.id, vocabulary_form_id=self.form.id,
                               example_id=self.example.id, reason="finnish_sentence", note="  sounds odd  ")
        self.assertEqual((report.status, report.note), ("open", "sounds odd"))
        self.assertEqual(report.snapshot["finnish_sentence"], "Mä juon kahvia.")
        self.assertEqual(self.example.validation_status, "needs_review")
        self.assertEqual(self.form.review_status, "active")

    def test_word_form_report_flags_form(self):
        create_report(self.session, content_id=self.word.id, vocabulary_form_id=self.form.id,
                      example_id=self.example.id, reason="word_form")
        self.assertEqual(self.form.review_status, "needs_review")
        self.assertEqual(self.example.validation_status, "auto_valid")

    def test_word_level_other_report(self):
        report = create_report(self.session, content_id=self.word.id, reason="other", note="")
        self.assertIsNone(report.note)
        self.assertEqual(report.snapshot, {"word": "kahvi"})

    def test_invalid_reports(self):
        with self.assertRaises(ReportNotFound):
            create_report(self.session, content_id=uuid4(), reason="other")
        with self.assertRaises(ReportNotFound):
            create_report(self.session, content_id=self.word.id, example_id=uuid4(), reason="translation")
        with self.assertRaises(ReportInvalid):
            create_report(self.session, content_id=self.word.id, reason="word_form")
        with self.assertRaises(ReportInvalid):
            create_report(self.session, content_id=self.word.id, example_id=self.example.id, reason="nonsense")

    def test_report_survives_example_deletion(self):
        report = create_report(self.session, content_id=self.word.id, example_id=self.example.id, reason="translation")
        self.session.delete(self.example)
        self.session.commit()
        self.session.refresh(report)
        self.assertIsNone(report.example_id)
        self.assertEqual(report.snapshot["english_translation"], "I drink coffee.")


if __name__ == "__main__":
    unittest.main()
