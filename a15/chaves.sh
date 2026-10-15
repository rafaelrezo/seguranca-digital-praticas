#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
umask 077
if [[ -e privada.pem || -e publica.pem ]]; then
  printf 'Par já existe. Os arquivos serão preservados; confira-os antes de continuar.\n'
  exit 1
fi
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out privada.pem
openssl pkey -in privada.pem -pubout -out publica.pem
ls -l privada.pem publica.pem
