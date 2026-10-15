#!/usr/bin/env bash
# Somente no gateway EC2 descartavel da A17. Reaplicar apos reboot.
set -euo pipefail
ALVO=10.77.2.10
POOL=10.8.0.0/24
CADEIA=A17_FORWARD
case "${1:-}" in
  aplicar)
    # Nao pressupor eth0: Ubuntu EC2 pode usar ens5 ou outro nome.
    INTERFACE=$(ip -4 route get "$ALVO" | awk '{for(i=1;i<=NF;i++) if($i=="dev") {print $(i+1); exit}}')
    [[ -n "$INTERFACE" && "$INTERFACE" != tun0 ]] || { echo 'Rota para a interna inesperada; pare.' >&2; exit 1; }
    ip -4 -o address show dev "$INTERFACE" | grep -q 'inet 10\.77\.1\.10/' || { echo 'Execute somente no gateway 10.77.1.10.' >&2; exit 1; }
    # Fechar forwarding durante a alteracao; SSH ao gateway usa INPUT/OUTPUT.
    sudo sysctl -w net.ipv4.ip_forward=0
    [[ $(sysctl -n net.ipv4.ip_forward) == 0 ]] || { echo 'Nao foi possivel desativar forwarding durante a configuracao.' >&2; exit 1; }
    # Cadeia exclusiva: nao limpa INPUT/OUTPUT nem regras de outros programas.
    if ! sudo iptables -nL "$CADEIA" >/dev/null 2>&1; then sudo iptables -N "$CADEIA"; fi
    sudo iptables -F "$CADEIA"
    sudo iptables -A "$CADEIA" -i tun0 -o "$INTERFACE" -s "$POOL" -d "$ALVO/32" -p tcp -m multiport --dports 22,8080 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
    sudo iptables -A "$CADEIA" -i "$INTERFACE" -o tun0 -s "$ALVO/32" -d "$POOL" -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    sudo iptables -A "$CADEIA" -j DROP
    if sudo iptables -C FORWARD -j "$CADEIA" 2>/dev/null; then sudo iptables -D FORWARD -j "$CADEIA"; fi
    sudo iptables -I FORWARD 1 -j "$CADEIA"
    sudo sysctl -w net.ipv4.ip_forward=1
    [[ $(sysctl -n net.ipv4.ip_forward) == 1 ]] || { echo 'Forwarding nao foi habilitado; pare antes de conectar.' >&2; exit 1; }
    echo 'Encaminhamento limitado a TCP 22/8080 na interna; sem NAT. Confira AWS ENI, SG e rota de retorno.'
    ;;
  inspecionar)
    ip -4 route get "$ALVO"
    sysctl net.ipv4.ip_forward
    sudo iptables -nvL "$CADEIA"
    sudo iptables -t nat -S
    ;;
  *) echo 'Somente gateway EC2. Uso: bash roteamento.sh aplicar|inspecionar' >&2; exit 2 ;;
esac
