#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
case "${1:-}" in
  preparar)
    cat claro.txt
    printf '\n'
    openssl version
    ;;
  cifrar)
    openssl enc -aes-256-cbc -salt -pbkdf2 -iter 10000 -in claro.txt -out copia.cbc
    ;;
  inspecionar)
    od -An -tx1 -N32 copia.cbc
    od -An -tc -N8 copia.cbc
    ;;
  abrir)
    openssl enc -d -aes-256-cbc -pbkdf2 -iter 10000 -in copia.cbc -out aberto.txt
    cat aberto.txt
    printf '\n'
    cmp claro.txt aberto.txt
    printf 'T2: bytes recuperados iguais ao original. CBC não verifica tag.\n'
    ;;
  *) printf 'Uso: bash cbc.sh preparar|cifrar|inspecionar|abrir\n' >&2; exit 2 ;;
esac
