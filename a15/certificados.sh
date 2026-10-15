#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
umask 077
case "${1:-}" in
  emitir)
    if [[ -e ca-chave-a15.pem || -e servidor-chave-a15.pem ]]; then
      echo 'Chaves já existem. Para outro ensaio use uma cópia nova da pasta, preservando o anterior.' >&2
      exit 1
    fi
    openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out ca-chave-a15.pem
    openssl req -new -x509 -key ca-chave-a15.pem -sha256 -days 2 -subj '/CN=CA-Lab-A15' -addext 'basicConstraints=critical,CA:TRUE' -addext 'keyUsage=critical,keyCertSign,cRLSign' -out ca-a15.pem
    openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out servidor-chave-a15.pem
    openssl req -new -key servidor-chave-a15.pem -subj '/CN=servidor.aula.invalid' -out servidor-pedido-a15.pem
    openssl x509 -req -in servidor-pedido-a15.pem -CA ca-a15.pem -CAkey ca-chave-a15.pem -CAcreateserial -days 2 -sha256 -extfile servidor-a15.ext -out servidor-a15.pem
    ;;
  inspecionar)
    openssl x509 -in servidor-a15.pem -noout -issuer -dates -ext subjectAltName,extendedKeyUsage
    ;;
  verificar)
    openssl verify -CAfile ca-a15.pem -purpose sslserver -verify_hostname servidor.aula.invalid servidor-a15.pem
    ;;
  nome-errado|sem-ca)
    [[ -r servidor-a15.pem && -r ca-a15.pem ]] || { echo 'Execute certificados.sh emitir antes.' >&2; exit 1; }
    args=(-purpose sslserver -verify_hostname servidor.aula.invalid)
    if [[ "$1" == nome-errado ]]; then
      args=(-CAfile ca-a15.pem -purpose sslserver -verify_hostname outro.aula.invalid)
    fi
    if openssl verify "${args[@]}" servidor-a15.pem; then
      echo 'INESPERADO: contraprova aceita.' >&2; exit 1
    fi
    echo 'Recusa esperada. Confira o motivo acima; arquivo ausente não prova recusa por confiança.'
    ;;
  *) echo 'Uso: bash certificados.sh emitir|inspecionar|verificar|nome-errado|sem-ca' >&2; exit 2 ;;
esac
