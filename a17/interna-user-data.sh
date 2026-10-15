#!/bin/bash
# Enviar como User data no console EC2 da maquina INTERNA Ubuntu 24.04.
# Executado por cloud-init como root no primeiro boot; nenhum download/apt.
set -euo pipefail
command -v python3
ip -4 -o address show | grep -q 'inet 10\.77\.2\.10/' || { echo 'IPv4 interno diferente do planejado.' >&2; exit 1; }
install -d -m 755 /opt/a17-servico
printf 'A17: maquina interna sem Internet\n' > /opt/a17-servico/index.html
chmod 644 /opt/a17-servico/index.html
if ! id a17-http >/dev/null 2>&1; then useradd --system --user-group --no-create-home --shell /usr/sbin/nologin a17-http; fi
cat > /etc/systemd/system/a17-http.service <<'EOF'
[Unit]
Description=A17 HTTP somente no IPv4 privado da maquina interna
After=network-online.target
Wants=network-online.target

[Service]
User=a17-http
Group=a17-http
ExecStart=/usr/bin/python3 -m http.server 8080 --bind 10.77.2.10 --directory /opt/a17-servico
Restart=on-failure
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now a17-http.service
