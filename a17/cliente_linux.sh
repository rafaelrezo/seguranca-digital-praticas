#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
case "${1:-original}" in
  original) perfil=cliente-a17.ovpn ;;
  nome-errado) perfil=cliente-nome-errado.ovpn ;;
  *) echo 'Uso: bash cliente_linux.sh original|nome-errado' >&2; exit 2 ;;
esac
exec sudo openvpn --config "$perfil"
