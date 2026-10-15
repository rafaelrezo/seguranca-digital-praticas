#!/usr/bin/env bash
set -euo pipefail
ip route get 10.8.0.1
curl --noproxy '*' --max-time 5 http://10.8.0.1:8080/
