#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
umask 077
case "${1:-}" in
  original)
    openssl dgst -sha256 -sign privada.pem -out assinatura.bin relatorio.txt
    openssl dgst -sha256 -verify publica.pem -signature assinatura.bin relatorio.txt
    ;;
  alterado)
    [[ -r publica.pem && -r assinatura.bin && -r alterado.txt ]] || { echo 'Execute chaves.sh e assinatura.sh original antes.' >&2; exit 1; }
    if openssl dgst -sha256 -verify publica.pem -signature assinatura.bin alterado.txt; then
      echo 'INESPERADO: mensagem alterada aceita.' >&2; exit 1
    fi
    echo 'V2: rejeição esperada; confira Verification failure acima.'
    ;;
  outra-chave)
    [[ -r assinatura.bin ]] || { echo 'Execute assinatura.sh original antes.' >&2; exit 1; }
    if [[ ! -e outra-privada.pem ]]; then
      openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out outra-privada.pem
    fi
    openssl pkey -in outra-privada.pem -pubout -out outra-publica.pem
    if openssl dgst -sha256 -verify outra-publica.pem -signature assinatura.bin relatorio.txt; then
      echo 'INESPERADO: outra chave aceita.' >&2; exit 1
    fi
    echo 'V3: rejeição esperada com a outra chave.'
    ;;
  *) echo 'Uso: bash assinatura.sh original|alterado|outra-chave' >&2; exit 2 ;;
esac
