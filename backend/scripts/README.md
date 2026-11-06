# Local scripts

From the `backend` directory, install the project dependencies:

```bash
source .venv/bin/activate
python -m pip install -e .
```

Set `OPENAI_API_KEY` in your own terminal session, then run:

```bash
python -m scripts.try_learning
```

The script uses a fixed sentence pattern and generates five exercises. It makes one API request for the model to choose suitable substitutions. Python fills those substitutions into the pattern and runs the remaining practice flow locally.

To apply database migrations and import the reviewed word-form pilot, run these from `backend/`:

```bash
alembic upgrade head
python -m scripts.import_vocabulary_forms
```

The import is idempotent and adds or refreshes the 232 word-form and usage targets in `data/vocabulary_forms_topic_1_3.json`. It expects the vocabulary topics and items to have already been imported.

To generate, validate, and save missing examples for a topic:

```bash
python -m scripts.generate_topic_examples --topic pronouns-and-reference --limit 10
```

Set `OPENAI_API_KEY` in the backend environment first. Each result includes a natural spoken Finnish sentence and its standard written counterpart; when the word is mainly written or has no register difference, the sentences can be identical. Prompts prioritize the common everyday sense, high-frequency concrete supporting words, and a simple main clause; they avoid abstract nominalizations and uncommon grammar. The script saves each result immediately, so later failures do not discard earlier examples. The limit supports reviewing a small pilot before generating the rest of a topic. Relational usage targets are saved as `needs_review` because the backend does not yet include a Finnish morphology analyzer; they do not count as covered until reviewed.

For an interactive terminal run that prompts for the key without echoing it, use:

```zsh
./scripts/generate_topic_examples.zsh
```

The default is the first topic and 10 missing targets. Optional arguments override them:

```zsh
./scripts/generate_topic_examples.zsh questions-and-connectors 20
```
