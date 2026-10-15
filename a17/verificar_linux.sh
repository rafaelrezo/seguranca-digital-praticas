#!/usr/bin/env bash
set -euo pipefail
ip route get 10.77.2.10
curl --noproxy '*' --max-time 5 http://10.77.2.10:8080/
