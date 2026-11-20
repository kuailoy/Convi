"""Tests for form-target generation. Run from backend/:

    python -m unittest tests.test_form_target_generation
"""

import copy
import csv
import json
import re
import tempfile
import unittest
from pathlib import Path

from app.services import form_target_generator as gen
from app.services.form_target_validator import LabelSet, normalize, validate_batch

BACKEND = Path(__file__).resolve().parents[1]
PROMPTS = BACKEND / "data-generation" / "form_targets" / "prompts"
LABELS = LabelSet.load(PROMPTS / f"{gen.PROMPT_VERSION}.labels.json")


def sample_batch():
    """A small accepted batch covering several parts of speech: (input_items, output)."""
    words = [
        ("talo", "noun", [("talon", "genitive_singular", "inflected_form"), ("taloa", "partitive_singular", "inflected_form"),
                          ("talossa", "inessive_singular", "inflected_form")]),
        ("koti", "noun", [("kodin", "genitive_singular", "inflected_form"), ("kotona", "related_location", "related_form"),
                          ("kotiin", "illative_singular", "inflected_form")]),
        ("antaa", "verb", [("annan", "present_1sg", "inflected_form"), ("antaa", "present_3sg", "inflected_form"),
                           ("antamaan", "third_infinitive_illative", "inflected_form"),
                           ("antaa lahjan", "accusative_complement", "governed_pattern")]),
        ("hyvä", "adjective", [("hyvän", "genitive_singular", "inflected_form"), ("parempi", "comparative", "inflected_form")]),
        ("hän", "pronoun", [("hänet", "accusative_singular", "inflected_form"), ("hänelle", "allative_singular", "inflected_form")]),
        ("ilman", "adposition", [("ilman kahvia", "partitive_complement", "governed_pattern")]),
        ("ja", "conjunction", []),
    ]
    inputs, items = [], []
    for number, (word, pos, forms) in enumerate(words, start=1):
        cid = f"00000000-0000-4000-8000-{number:012d}"
        inputs.append({"content_id": cid, "word": word, "part_of_speech": pos, "pos_subtype": None})
        items.append({"content_id": cid, "word": word, "forms": [
            {"form": f, "grammatical_label": l, "target_type": tt, "notes": ""} for f, l, tt in forms]})
    return inputs, {"items": items}


def one_item(word, pos, forms, subtype=None):
    cid = "00000000-0000-4000-8000-000000000001"
    inputs = [{"content_id": cid, "word": word, "part_of_speech": pos, "pos_subtype": subtype}]
    output = {"items": [{"content_id": cid, "word": word, "forms": [
        {"form": f, "grammatical_label": l, "target_type": t, "notes": ""} for f, l, t in forms]}]}
    return inputs, output


def codes(issues):
    return {issue.code for issue in issues}


class LabelFileTest(unittest.TestCase):
    def test_labels_file_matches_prompt(self):
        prompt = (PROMPTS / f"{gen.PROMPT_VERSION}.md").read_text(encoding="utf-8")
        section = prompt.split("## Allowed labels")[1].split("## Part-of-speech guidance")[0]
        in_prompt = set(re.findall(r"`([a-z0-9]+(?:_[a-z0-9]+)+)`", section)) | {
            w for w in ("comparative", "superlative") if f"`{w}`" in section}
        self.assertEqual(LABELS.labels - in_prompt, set(), "labels missing from the prompt")
        extra = {label for label in in_prompt - LABELS.labels if not LABELS.allows(label)}
        self.assertEqual(extra, set(), "prompt labels missing from the labels file")

    def test_possessive_pattern_for_itse(self):
        self.assertTrue(LABELS.allows("partitive_singular_possessive_1sg"))
        self.assertFalse(LABELS.allows("genitive_singular_possessive_1sg"))


class ValidatorTest(unittest.TestCase):
    def test_valid_batch_passes(self):
        inputs, output = sample_batch()
        result = validate_batch(inputs, output, LABELS)
        self.assertEqual(result.errors, [])

    def assert_error(self, code, word, pos, forms, subtype=None):
        inputs, output = one_item(word, pos, forms, subtype)
        self.assertIn(code, codes(validate_batch(inputs, output, LABELS).errors))

    def test_headword_spelling(self):
        inputs, output = one_item("antaa", "verb", [("annan", "present_1sg", "inflected_form"),
                                                     ("antaa", "present_3sg", "inflected_form")])
        self.assertEqual(validate_batch(inputs, output, LABELS).errors, [])
        self.assert_error("headword", "ei", "verb", [("ei", "negative_verb_3sg", "inflected_form")],
                          subtype="negative_auxiliary")
        self.assert_error("headword", "koti", "noun", [("koti", "related_location", "related_form")])

    def test_accusative_complement(self):
        inputs, output = one_item("ostaa", "verb", [("ostan", "present_1sg", "inflected_form"),
                                                     ("ostaa auton", "accusative_complement", "governed_pattern")])
        self.assertEqual(validate_batch(inputs, output, LABELS).errors, [])

    def test_duplicate_form_and_label(self):
        self.assert_error("duplicate_form", "talo", "noun", [
            ("talon", "genitive_singular", "inflected_form"), ("talon", "partitive_singular", "inflected_form")])
        self.assert_error("duplicate_label", "talo", "noun", [
            ("talon", "genitive_singular", "inflected_form"), ("talojen", "genitive_singular", "inflected_form")])

    def test_unknown_label_and_wrong_type(self):
        self.assert_error("label", "talo", "noun", [("talon", "genitive_sg", "inflected_form")])
        self.assert_error("label_type", "koti", "noun", [("kotona", "related_location", "inflected_form")])
        self.assert_error("target_type", "ja", "conjunction", [("ja", "invariant", "invariant")])

    def test_multiword_inflected_form(self):
        self.assert_error("multiword", "puhua", "verb", [("olen puhunut", "past_participle", "inflected_form")])

    def test_patterns(self):
        self.assert_error("pattern_headword", "kanssa", "adposition",
                          [("minun kanssani", "genitive_complement", "governed_pattern")])
        self.assert_error("verb_pattern", "pitää", "verb",
                          [("pitää paljon kahvista", "elative_complement", "governed_pattern")])
        inputs, output = one_item("pitää", "verb", [
            ("pidän", "present_1sg", "inflected_form"), ("pitää kahvista", "elative_complement", "governed_pattern")])
        self.assertEqual(validate_batch(inputs, output, LABELS).errors, [])

    def test_items_mismatch(self):
        inputs, output = sample_batch()
        output["items"] = output["items"][1:]
        self.assertIn("items_mismatch", codes(validate_batch(inputs, output, LABELS).errors))

    def test_warnings(self):
        inputs, output = one_item("paljon", "adverb", [("enemmän", "comparative", "inflected_form")])
        result = validate_batch(inputs, output, LABELS, {normalize("enemmän"), normalize("paljon")})
        self.assertEqual(result.errors, [])
        self.assertTrue({"other_headword", "label_pos"} <= codes(result.warnings))
        inputs, output = one_item("ja", "conjunction", [])
        self.assertEqual(codes(validate_batch(inputs, output, LABELS).warnings), set())
        inputs, output = one_item("täytyä", "verb", [("täytyy", "present_3sg", "inflected_form")])
        self.assertNotIn("verb_no_present", codes(validate_batch(inputs, output, LABELS).warnings))


class PlanningTest(unittest.TestCase):
    def test_split_sizes(self):
        self.assertEqual(gen.split_sizes(9, 15), [9])
        self.assertEqual(gen.split_sizes(20, 15), [20])
        self.assertEqual(gen.split_sizes(29, 15), [15, 14])
        self.assertEqual(gen.split_sizes(49, 15), [13, 12, 12, 12])

    def test_pilot_plan(self):
        rows = gen.load_vocabulary(gen.VOCABULARY_CSV)
        topics = gen.resolve_topics("pilot", rows, gen.SETS_DIR)
        batches = gen.plan_batches(rows, topics, 15)
        self.assertEqual(len(batches), 5)
        self.assertEqual(sum(len(b["content_ids"]) for b in batches), 68)


class RunTest(unittest.TestCase):
    """Full run with a fake model: generation, failure, retry and resume."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.paths = gen.Paths(outputs_dir=self.tmp, corrections=self.tmp / "corrections.json")
        self.calls = 0
        self.break_next = False

    def fake_model(self, instructions, input_text, schema):
        self.calls += 1
        items = json.loads(input_text)["items"]
        output = {"items": [{"content_id": i["content_id"], "word": i["word"], "forms": []} for i in items]}
        if self.break_next:
            output["items"][0]["forms"] = [{"form": items[0]["word"] + "n", "grammatical_label": "genitive_sg",
                                            "target_type": "inflected_form", "notes": ""}]
        return json.dumps(output), {"input_tokens": 1, "output_tokens": 1}

    def run_topic(self, **kwargs):
        return gen.run("topic:food-and-drink", caller=self.fake_model, paths=self.paths, log=lambda _: None, **kwargs)

    def test_failure_retry_and_resume(self):
        self.break_next = True
        summary = self.run_topic()
        self.assertEqual((summary.failed, self.calls), (1, gen.VALIDATION_ATTEMPTS))
        self.assertTrue(list((summary.output_dir / "errors").glob("*.txt")))

        self.break_next = False
        self.run_topic()  # failed batches are not retried without the flag
        self.assertEqual(self.calls, gen.VALIDATION_ATTEMPTS)
        summary = self.run_topic(retry_failed=True)
        self.assertEqual(summary.done, 1)

        calls = self.calls
        self.run_topic()  # resume: nothing left to do
        self.assertEqual(self.calls, calls)

        with (summary.output_dir / "combined.csv").open(encoding="utf-8") as handle:
            self.assertEqual(len(list(csv.DictReader(handle))), 9)  # one empty row per word

    def test_removed_batch_files_keep_combined(self):
        summary = self.run_topic()
        combined = (summary.output_dir / "combined.json").read_text(encoding="utf-8")
        for path in (summary.output_dir / "batches").glob("*.json"):
            path.unlink()
        summary = self.run_topic()
        self.assertEqual((summary.done, summary.corrections_applied), (1, 0))
        self.assertEqual((summary.output_dir / "combined.json").read_text(encoding="utf-8"), combined)

    def test_dry_run_calls_nothing(self):
        summary = self.run_topic(dry_run=True)
        self.assertEqual((self.calls, summary.pending), (0, 1))
        self.assertTrue((summary.output_dir / "inputs" / "food-and-drink__01.json").exists())

    def test_corrections(self):
        (self.tmp / "corrections.json").write_text(json.dumps({"corrections": [
            {"word": "kahvi", "action": "add", "form": "kahvia", "grammatical_label": "partitive_singular",
             "target_type": "inflected_form"},
            {"word": "kahvi", "action": "add", "form": "kahvin", "grammatical_label": "genitive_singular",
             "target_type": "inflected_form"},
            {"word": "vesi", "action": "remove", "form": "nothing-to-remove"},
        ]}), encoding="utf-8")
        summary = self.run_topic()
        self.assertEqual(summary.corrections_applied, 2)
        combined = json.loads((summary.output_dir / "combined.json").read_text(encoding="utf-8"))
        kahvi = next(i for i in combined["items"] if i["word"] == "kahvi")
        self.assertEqual([(f["form"], f["source"]) for f in kahvi["forms"]],
                         [("kahvia", "correction"), ("kahvin", "correction")])

    def test_invalid_corrections_stop(self):
        (self.tmp / "corrections.json").write_text(json.dumps({"corrections": [
            {"word": "kahvi", "action": "add", "form": "kahvia", "grammatical_label": "partitive_sg",
             "target_type": "inflected_form"}]}), encoding="utf-8")
        with self.assertRaises(gen.StopRun):
            self.run_topic(dry_run=True)

    def test_reuse_batches_from_another_set(self):
        self.run_topic()
        calls = self.calls
        summary = gen.run("pilot", caller=self.fake_model, paths=self.paths, log=lambda _: None,
                          dry_run=True, reuse="topic:food-and-drink")
        self.assertEqual((summary.reused, summary.done, self.calls), (1, 1, calls))

    def test_changed_settings_stop(self):
        self.run_topic(dry_run=True)
        with self.assertRaises(gen.StopRun):
            self.run_topic(dry_run=True, model="another-model")


if __name__ == "__main__":
    unittest.main()
