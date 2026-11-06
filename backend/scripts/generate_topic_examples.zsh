#!/bin/zsh

set -e

script_dir=${0:A:h}
backend_dir=${script_dir:h}
topic=${1:-pronouns-and-reference}
limit=${2:-10}

cd "$backend_dir"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  read -rs "OPENAI_API_KEY?OpenAI API key: "
  print
  export OPENAI_API_KEY
fi

exec .venv/bin/python -m scripts.generate_topic_examples \
  --topic "$topic" \
  --limit "$limit"