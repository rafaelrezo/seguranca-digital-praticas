#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p servico
printf 'A17: servico de teste no tunel\n' > servico/index.html
exec python3 -m http.server 8080 --bind 10.8.0.1 --directory servico
