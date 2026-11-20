"""Batch generation of Finnish form targets (current prompt: PROMPT_VERSION).

Reads the vocabulary classification CSV, splits a set of topics into batches,
calls the model, validates each response and writes local files. Progress is
kept in a manifest so that an interrupted run can be resumed by running the
same command again. Nothing is written to the database.

Design: docs/data-generation/form-target-batch-tool.md
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from app.services.form_target_validator import Issue, LabelSet, ValidationResult, normalize, validate_batch
from app.services.voikko_check import VoikkoChecker

PROMPT_VERSION = "form_generation_v3"
DEFAULT_MODEL = "gpt-6-luna"
DEFAULT_BATCH_SIZE = 15
SINGLE_BATCH_LIMIT = 20
VALIDATION_ATTEMPTS = 2  # first attempt + one retry per run
API_ATTEMPTS = 3

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data-generation"
VOCABULARY_CSV = DATA_DIR / "vocabulary" / "vocabulary_classification.csv"
FORM_TARGETS_DIR = DATA_DIR / "form_targets"
PROMPTS_DIR = FORM_TARGETS_DIR / "prompts"
SETS_DIR = FORM_TARGETS_DIR / "sets"
OUTPUTS_DIR = FORM_TARGETS_DIR / "outputs"


class StopRun(Exception):
    """A problem that makes continuing pointless (bad key, changed inputs, ...)."""


@dataclass(frozen=True)
class Paths:
    vocabulary_csv: Path = VOCABULARY_CSV
    prompt: Path = PROMPTS_DIR / f"{PROMPT_VERSION}.md"
    schema: Path = PROMPTS_DIR / f"{PROMPT_VERSION}.schema.json"
    labels: Path = PROMPTS_DIR / f"{PROMPT_VERSION}.labels.json"
    corrections: Path = FORM_TARGETS_DIR / "corrections.json"
    sets_dir: Path = SETS_DIR
    outputs_dir: Path = OUTPUTS_DIR


# A model caller takes (instructions, input_text, schema) and returns (output_text, usage dict).
ModelCaller = Callable[[str, str, dict], tuple[str, dict]]


# ---------------------------------------------------------------- planning

def load_vocabulary(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["word"] = unicodedata.normalize("NFC", row["word"])
    return rows


def resolve_topics(set_name: str, rows: list[dict], sets_dir: Path) -> list[str]:
    all_topics = list(dict.fromkeys(row["topic_slug"] for row in rows))
    if set_name == "all":
        return all_topics
    if set_name.startswith("topic:"):
        topics = [set_name.removeprefix("topic:")]
    else:
        set_file = sets_dir / f"{set_name}.json"
        if not set_file.exists():
            raise StopRun(f"Unknown set '{set_name}': no file {set_file}.")
        topics = json.loads(set_file.read_text(encoding="utf-8"))["topics"]
    unknown = [t for t in topics if t not in all_topics]
    if unknown:
        raise StopRun(f"Unknown topic slug(s): {', '.join(unknown)}.")
    return topics


def split_sizes(count: int, batch_size: int) -> list[int]:
    if count <= SINGLE_BATCH_LIMIT:
        return [count]
    parts = math.ceil(count / batch_size)
    base, extra = divmod(count, parts)
    return [base + 1 if i < extra else base for i in range(parts)]


def plan_batches(rows: list[dict], topics: list[str], batch_size: int) -> list[dict]:
    batches = []
    for topic in topics:
        topic_rows = [row for row in rows if row["topic_slug"] == topic]
        start = 0
        for number, size in enumerate(split_sizes(len(topic_rows), batch_size), start=1):
            chunk = topic_rows[start : start + size]
            start += size
            batches.append(
                {
                    "batch_id": f"{topic}__{number:02d}",
                    "topic_slug": topic,
                    "content_ids": [row["id"] for row in chunk],
                    "status": "pending",
                    "attempts": 0,
                    "warnings": 0,
                    "last_error": None,
                    "completed_at": None,
                    "usage": None,
                }
            )
    return batches


def model_input_items(rows: list[dict]) -> list[dict]:
    return [
        {
            "content_id": row["id"],
            "word": row["word"],
            "part_of_speech": row["part_of_speech"],
            "pos_subtype": row["pos_subtype"] or None,
            "verb_type": row["verb_type"] or None,
            "topic_name": row["topic_name_en"],
            "topic_slug": row["topic_slug"],
        }
        for row in rows
    ]


# ---------------------------------------------------------------- files

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, data: object) -> None:
    """Write atomically: a crash never leaves a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def output_dir_for(set_name: str, outputs_dir: Path) -> Path:
    name = set_name.replace("topic:", "topic_")
    version = PROMPT_VERSION.rsplit("_", 1)[-1]  # "v3"
    return outputs_dir / f"{version}_{name}"


# ---------------------------------------------------------------- model

def openai_caller(model: str) -> ModelCaller:
    import openai

    client = openai.OpenAI()
    transient = (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError, openai.InternalServerError)
    fatal = (openai.AuthenticationError, openai.PermissionDeniedError, openai.BadRequestError, openai.NotFoundError)

    def call(instructions: str, input_text: str, schema: dict) -> tuple[str, dict]:
        for attempt in range(1, API_ATTEMPTS + 1):
            try:
                response = client.responses.create(
                    model=model,
                    instructions=instructions,
                    input=input_text,
                    text={"format": {"type": "json_schema", "name": "form_targets", "strict": True, "schema": schema}},
                )
            except fatal as error:
                raise StopRun(f"OpenAI rejected the request: {error.__class__.__name__}: {error}") from error
            except transient as error:
                if attempt == API_ATTEMPTS:
                    raise RuntimeError(f"API error after {attempt} attempts: {error.__class__.__name__}") from error
                time.sleep(2 ** attempt)
                continue
            usage = getattr(response, "usage", None)
            return response.output_text, {
                "input_tokens": getattr(usage, "input_tokens", None),
                "output_tokens": getattr(usage, "output_tokens", None),
            }
        raise AssertionError("unreachable")

    return call


# ---------------------------------------------------------------- run

@dataclass
class RunSummary:
    output_dir: Path
    planned: int
    done: int
    failed: int
    pending: int
    ran: int
    warnings: int
    reused: int = 0
    corrections_applied: int = 0


def run(
    set_name: str,
    *,
    model: str = DEFAULT_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    retry_failed: bool = False,
    only: str | None = None,
    dry_run: bool = False,
    reuse: str | None = None,
    caller: ModelCaller | None = None,
    paths: Paths = Paths(),
    log: Callable[[str], None] = print,
) -> RunSummary:
    rows = load_vocabulary(paths.vocabulary_csv)
    by_id = {row["id"]: row for row in rows}
    all_headwords = {normalize(row["word"]) for row in rows}
    topics = resolve_topics(set_name, rows, paths.sets_dir)
    planned = plan_batches(rows, topics, batch_size)

    instructions = paths.prompt.read_text(encoding="utf-8")
    schema = json.loads(paths.schema.read_text(encoding="utf-8"))
    labels = LabelSet.load(paths.labels)
    versions = {
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": sha256(paths.prompt),
        "schema_sha256": sha256(paths.schema),
        "labels_sha256": sha256(paths.labels),
        "model": model,
        "batch_size": batch_size,
    }

    out = output_dir_for(set_name, paths.outputs_dir)
    manifest_path = out / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        _check_manifest(manifest, versions, planned)
    else:
        manifest = {"set": set_name, **versions, "created_at": now(), "batches": planned}

    corrections = load_corrections(paths.corrections, by_id, labels)
    reused = _reuse_batches(reuse, manifest, versions, out, paths, log) if reuse else 0
    if reused:
        write_json(manifest_path, manifest)

    if only and only not in {b["batch_id"] for b in manifest["batches"]}:
        raise StopRun(f"No batch '{only}' in this set.")

    if dry_run:
        write_json(manifest_path, manifest)
        for batch in manifest["batches"]:  # what the model would receive, for inspection
            items = model_input_items([by_id[cid] for cid in batch["content_ids"]])
            write_json(out / "inputs" / f"{batch['batch_id']}.json", {"items": items})
        for batch in manifest["batches"]:
            log(f"  {batch['batch_id']}: {len(batch['content_ids'])} words, {batch['status']}")
        log(f"Dry run: plan and inputs written to {out}")
        return _summary(out, manifest, ran=0, reused=reused)

    ran = 0
    voikko = None
    for batch in manifest["batches"]:
        if only and batch["batch_id"] != only:
            continue
        if not only and not (batch["status"] == "pending" or (retry_failed and batch["status"] == "failed")):
            continue
        ran += 1
        if caller is None:  # created lazily: a run with nothing left to do needs no API key
            caller = openai_caller(model)
        if voikko is None:
            voikko = VoikkoChecker.create() or False
            log("Voikko check: " + ("on" if voikko else "off (libvoikko not installed)"))
        items = model_input_items([by_id[cid] for cid in batch["content_ids"]])
        input_text = json.dumps({"items": items}, ensure_ascii=False, indent=2)
        log(f"{batch['batch_id']} ({len(items)} words) ...")
        _run_batch(batch, items, input_text, instructions, schema, labels, all_headwords, caller, out, model, log,
                   voikko or None)
        write_json(manifest_path, manifest)

    write_json(manifest_path, manifest)
    done = [b for b in manifest["batches"] if b["status"] == "done"]
    if any(not (out / "batches" / f"{b['batch_id']}.json").exists() for b in done):
        # A finished, imported set may have its batch files removed: combined.json is then the final data.
        log("Batch files have been removed; combined files are left unchanged.")
        applied = 0
    else:
        applied = _write_combined(out, manifest, by_id, corrections)
    return _summary(out, manifest, ran, reused=reused, corrections_applied=applied)


def _run_batch(batch, items, input_text, instructions, schema, labels, all_headwords, caller, out, model, log,
               voikko=None):
    for _ in range(VALIDATION_ATTEMPTS):
        batch["attempts"] += 1
        attempt = batch["attempts"]
        try:
            text, usage = caller(instructions, input_text, schema)
        except StopRun:
            raise
        except Exception as error:  # API failure after retries: record and move on
            batch.update(status="failed", last_error=str(error))
            log(f"  failed: {error}")
            return
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as error:
            result = ValidationResult()
            result.errors.append(Issue("json", f"Response is not valid JSON: {error}"))
            parsed = None
        else:
            result = validate_batch(items, parsed, labels, all_headwords, voikko)

        if result.ok:
            write_json(
                out / "batches" / f"{batch['batch_id']}.json",
                {
                    "batch_id": batch["batch_id"],
                    "prompt_version": PROMPT_VERSION,
                    "model": model,
                    "generated_at": now(),
                    "usage": usage,
                    "warnings": [w.as_dict() for w in result.warnings],
                    "output": parsed,
                },
            )
            batch.update(status="done", warnings=len(result.warnings), last_error=None, completed_at=now(), usage=usage)
            log(f"  done ({len(result.warnings)} warnings)")
            return

        error_file = out / "errors" / f"{batch['batch_id']}.{attempt}.txt"
        error_file.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"{e.code}: {e.message} [{e.content_id or '-'} {e.form or ''}]".rstrip() for e in result.errors]
        error_file.write_text("\n".join(lines) + "\n\n--- raw response ---\n" + text + "\n", encoding="utf-8")
        batch.update(status="failed", last_error=f"{len(result.errors)} validation errors, see {error_file.name}")
        log(f"  attempt {attempt}: {len(result.errors)} validation errors ({error_file.name})")


def _check_manifest(manifest: dict, versions: dict, planned: list[dict]) -> None:
    changed = [key for key, value in versions.items() if manifest.get(key) != value]
    if changed:
        raise StopRun(
            "This output directory was created with a different "
            + ", ".join(changed)
            + ". Use a new output directory (or move the old one) instead of mixing versions."
        )
    old = {b["batch_id"]: b["content_ids"] for b in manifest["batches"]}
    new = {b["batch_id"]: b["content_ids"] for b in planned}
    if old != new:
        differing = sorted(k for k in old.keys() | new.keys() if old.get(k) != new.get(k))
        raise StopRun("The vocabulary or set changed since this run started; batches differ: " + ", ".join(differing))


def _write_combined(out: Path, manifest: dict, by_id: dict, corrections: list[dict]) -> int:
    combined_items = []
    csv_rows = []
    applied = 0
    for batch in manifest["batches"]:
        if batch["status"] != "done":
            continue
        data = json.loads((out / "batches" / f"{batch['batch_id']}.json").read_text(encoding="utf-8"))
        warnings = data["warnings"]
        for raw_item in data["output"]["items"]:
            item, count = apply_corrections(raw_item, corrections)
            applied += count
            source = by_id[item["content_id"]]
            combined_items.append({**item, "part_of_speech": source["part_of_speech"], "topic_slug": source["topic_slug"]})
            item_warnings = [w for w in warnings if w["content_id"] == item["content_id"] and not w["form"]]
            base = {
                "batch_id": batch["batch_id"],
                "topic_slug": source["topic_slug"],
                "content_id": item["content_id"],
                "word": item["word"],
                "part_of_speech": source["part_of_speech"],
            }
            if not item["forms"]:
                csv_rows.append({**base, "display_order": "", "form": "", "grammatical_label": "",
                                 "target_type": "", "notes": "", "source": "", "warnings": _join(item_warnings)})
            for order, target in enumerate(item["forms"], start=1):
                form_warnings = [w for w in warnings if w["content_id"] == item["content_id"] and w["form"] == target["form"]]
                csv_rows.append({**base, "display_order": order, **target,
                                 "warnings": _join(form_warnings + item_warnings)})
    write_json(out / "combined.json", {"prompt_version": PROMPT_VERSION, "items": combined_items})
    columns = ["batch_id", "topic_slug", "content_id", "word", "part_of_speech", "display_order",
               "form", "grammatical_label", "target_type", "notes", "source", "warnings"]
    tmp = out / "combined.csv.tmp"
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(csv_rows)
    os.replace(tmp, out / "combined.csv")
    return applied


def _join(warnings: list[dict]) -> str:
    return "; ".join(f"{w['code']}: {w['message']}" for w in warnings)


def _summary(out: Path, manifest: dict, ran: int, reused: int = 0, corrections_applied: int = 0) -> RunSummary:
    statuses = [b["status"] for b in manifest["batches"]]
    return RunSummary(
        output_dir=out,
        planned=len(statuses),
        done=statuses.count("done"),
        failed=statuses.count("failed"),
        pending=statuses.count("pending"),
        ran=ran,
        warnings=sum(b["warnings"] for b in manifest["batches"]),
        reused=reused,
        corrections_applied=corrections_applied,
    )


# ---------------------------------------------------------------- reuse and corrections

def _reuse_batches(reuse: str, manifest: dict, versions: dict, out: Path, paths: Paths, log) -> int:
    """Copy accepted batches with identical words from another set made with the same prompt and model."""
    src = output_dir_for(reuse, paths.outputs_dir)
    src_manifest_path = src / "manifest.json"
    if not src_manifest_path.exists():
        raise StopRun(f"Nothing to reuse: no manifest in {src}.")
    src_manifest = json.loads(src_manifest_path.read_text(encoding="utf-8"))
    changed = [k for k, v in versions.items() if src_manifest.get(k) != v]
    if changed:
        raise StopRun(f"Cannot reuse {src.name}: it was made with a different " + ", ".join(changed) + ".")
    done = {b["batch_id"]: b for b in src_manifest["batches"] if b["status"] == "done"}
    reused = 0
    for batch in manifest["batches"]:
        source = done.get(batch["batch_id"])
        if batch["status"] == "done" or not source or source["content_ids"] != batch["content_ids"]:
            continue
        if not (src / "batches" / f"{batch['batch_id']}.json").exists():
            continue
        target = out / "batches" / f"{batch['batch_id']}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((src / "batches" / f"{batch['batch_id']}.json").read_bytes())
        batch.update(status="done", attempts=source["attempts"], warnings=source["warnings"], last_error=None,
                     completed_at=source["completed_at"], usage=source["usage"], reused_from=src.name)
        reused += 1
    log(f"Reused {reused} batches from {src.name}.")
    return reused


CORRECTION_ACTIONS = {"add", "remove", "replace"}


def load_corrections(path: Path, by_id: dict, labels: LabelSet) -> list[dict]:
    """Manual corrections, applied on top of accepted model output (which is never edited).

    Each entry names the word and an action:
      add:     form, grammatical_label, target_type, optional notes  (skipped if the form is already there)
      remove:  form                                                  (skipped if absent)
      replace: form, new_form                                        (skipped if absent)
    """
    if not path.exists():
        return []
    entries = json.loads(path.read_text(encoding="utf-8")).get("corrections", [])
    words = {normalize(row["word"]): row["id"] for row in by_id.values()}
    problems = []
    for number, entry in enumerate(entries, start=1):
        action = entry.get("action")
        if action not in CORRECTION_ACTIONS:
            problems.append(f"#{number}: unknown action '{action}'")
            continue
        if normalize(entry.get("word", "")) not in words:
            problems.append(f"#{number}: unknown word '{entry.get('word')}'")
        if not entry.get("form"):
            problems.append(f"#{number}: missing form")
        if action == "replace" and not entry.get("new_form"):
            problems.append(f"#{number}: replace needs new_form")
        if action == "add":
            label, ttype = entry.get("grammatical_label", ""), entry.get("target_type", "")
            if not labels.allows(label):
                problems.append(f"#{number}: label '{label}' is not allowed")
            elif labels.expected_target_type(label) != ttype:
                problems.append(f"#{number}: label '{label}' needs target_type '{labels.expected_target_type(label)}'")
        entry["content_id"] = words.get(normalize(entry.get("word", "")))
    if problems:
        raise StopRun(f"Invalid corrections in {path.name}: " + "; ".join(problems))
    return entries


def apply_corrections(item: dict, corrections: list[dict]) -> tuple[dict, int]:
    forms = [{**target, "source": "model"} for target in item["forms"]]
    applied = 0
    for entry in corrections:
        if entry["content_id"] != item["content_id"]:
            continue
        index = next((i for i, t in enumerate(forms) if normalize(t["form"]) == normalize(entry["form"])), None)
        if entry["action"] == "add" and index is None:
            forms.append({"form": entry["form"], "grammatical_label": entry["grammatical_label"],
                          "target_type": entry["target_type"], "notes": entry.get("notes", ""), "source": "correction"})
            applied += 1
        elif entry["action"] == "remove" and index is not None:
            forms.pop(index)
            applied += 1
        elif entry["action"] == "replace" and index is not None:
            forms[index] = {**forms[index], "form": entry["new_form"], "source": "correction"}
            applied += 1
    return {**item, "forms": forms}, applied
