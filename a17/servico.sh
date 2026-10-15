#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
echo 'O servico agora roda na segunda EC2, em 10.77.2.10:8080.'
echo 'Use interna-user-data.sh no lancamento pelo console. Este script antigo nao inicia HTTP no gateway.'
exit 2
