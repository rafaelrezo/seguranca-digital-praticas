#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
case "${1:-}" in
  hash) sha256sum hash-a.txt hash-b.txt ;;
  hmac)
    openssl dgst -sha256 -hmac 'chave-aula-descartavel' msg-a.txt
    openssl dgst -sha256 -hmac 'chave-aula-descartavel' msg-a.txt
    ;;
  mensagem-alterada) openssl dgst -sha256 -hmac 'chave-aula-descartavel' msg-a.txt msg-b.txt ;;
  chave-alterada)
    openssl dgst -sha256 -hmac 'chave-aula-descartavel' msg-a.txt
    openssl dgst -sha256 -hmac 'outra-chave-aula' msg-a.txt
    ;;
  *) echo 'Uso: bash hash_hmac.sh hash|hmac|mensagem-alterada|chave-alterada' >&2; exit 2 ;;
esac
