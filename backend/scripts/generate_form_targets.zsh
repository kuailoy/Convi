#!/bin/zsh
# Usage: ./scripts/generate_form_targets.zsh topic:food-and-drink [extra options]

set -e

script_dir=${0:A:h}
backend_dir=${script_dir:h}
set_name=${1:-pilot}
shift || true

cd "$backend_dir"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  read -rs "OPENAI_API_KEY?OpenAI API key: "
  print
  export OPENAI_API_KEY
fi

exec .venv/bin/python -m scripts.generate_form_targets --set "$set_name" "$@"
