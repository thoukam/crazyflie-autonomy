#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    printf 'Utilise: source scripts/activate.sh\n' >&2
    exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
activate_file="${script_dir}/../.venv/bin/activate"

if [[ ! -f "$activate_file" ]]; then
    printf 'Environnement virtuel introuvable: %s\n' "$activate_file" >&2
    return 1
fi

source "$activate_file"
unset script_dir activate_file
