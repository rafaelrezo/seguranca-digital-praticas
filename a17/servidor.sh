#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
umask 077
case "${1:-}" in
  preparar)
    sudo apt update
    sudo apt install openvpn python3
    openvpn --version
    [[ -c /dev/net/tun ]] || { echo 'TUN ausente; pare antes de configurar.' >&2; exit 1; }
    if [[ ! -e ta.key ]]; then openvpn --genkey tls-auth ta.key; fi
    echo 'TUN disponível; ta.key criado ou preservado.'
    ;;
  configurar)
    for arquivo in ca.crt servidor.crt servidor.key crl.pem server.conf ta.key; do
      [[ -r "$arquivo" ]] || { echo "Arquivo ausente: $arquivo" >&2; exit 1; }
    done
    sudo install -d -m 755 /etc/openvpn/server
    sudo install -m 644 ca.crt servidor.crt crl.pem server.conf /etc/openvpn/server/
    sudo install -m 600 servidor.key ta.key /etc/openvpn/server/
    echo 'Configuração instalada. Inicie o servidor na próxima etapa.'
    ;;
  iniciar) exec sudo openvpn --cd /etc/openvpn/server --config server.conf ;;
  atualizar-crl)
    openssl crl -in crl.pem -noout -verify -CAfile ca.crt
    sudo install -m 644 crl.pem /etc/openvpn/server/crl.pem
    openssl crl -in /etc/openvpn/server/crl.pem -noout -issuer -lastupdate -nextupdate
    echo 'CRL instalada. Reinicie explicitamente o servidor de laboratório antes da nova conexão.'
    ;;
  *) echo 'Somente EC2 Ubuntu. Uso: bash servidor.sh preparar|configurar|iniciar|atualizar-crl' >&2; exit 2 ;;
esac
