#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
endereco="127.0.0.1:${A16_TLS_PORT:-8443}"
ca=../a15/ca-a15.pem
case "${1:-}" in
  servidor)
    exec openssl s_server -accept "$endereco" -cert ../a15/servidor-a15.pem -key ../a15/servidor-chave-a15.pem -tls1_3 -www
    ;;
  handshake)
    if ! openssl s_client -connect "$endereco" -servername servidor.aula.invalid -CAfile "$ca" -verify_hostname servidor.aula.invalid -verify_return_error -tls1_3 -groups X25519 -msg -brief </dev/null > tls-a16.txt 2>&1; then
      cat tls-a16.txt >&2; exit 1
    fi
    grep -E 'Handshake|Protocol version:|Ciphersuite:|Verification:' tls-a16.txt
    ;;
  nome-errado)
    [[ -r "$ca" ]] || { echo 'Emita os certificados da A15 antes.' >&2; exit 1; }
    if openssl s_client -connect "$endereco" -servername servidor.aula.invalid -CAfile "$ca" -verify_hostname outro.aula.invalid -verify_return_error -tls1_3 -brief </dev/null > tls-a16.txt 2>&1; then
      echo 'INESPERADO: nome incorreto aceito.' >&2; exit 1
    fi
    cat tls-a16.txt
    grep -q 'hostname mismatch' tls-a16.txt || { echo 'Falha diferente da contraprova de nome; confira o servidor e o erro.' >&2; exit 1; }
    ;;
  http)
    printf 'GET / HTTP/1.0\r\nHost: servidor.aula.invalid\r\n\r\n' | openssl s_client -connect "$endereco" -servername servidor.aula.invalid -CAfile "$ca" -verify_hostname servidor.aula.invalid -verify_return_error -tls1_3 -quiet
    ;;
  publico)
    openssl s_client -connect rafaelrezo.github.io:443 -servername rafaelrezo.github.io -verify_hostname rafaelrezo.github.io -verify_return_error -brief </dev/null
    ;;
  *) echo 'Uso: bash tls.sh servidor|handshake|nome-errado|http|publico' >&2; exit 2 ;;
esac
