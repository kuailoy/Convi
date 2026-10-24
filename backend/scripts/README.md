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
