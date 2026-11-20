# Tests

Standard-library `unittest`, no database needed (SQLite in memory). Run all from `backend/`:

```bash
python -m unittest discover tests
```

| File | Covers |
| --- | --- |
| `test_form_target_generation.py` | Validator rules, batch planning, resume, reuse, corrections (form-target generation tool) |
| `test_form_target_import.py` | Headword targets and replacing `vocabulary_forms` on import |
| `test_content_reports.py` | Problem reports from the app |
