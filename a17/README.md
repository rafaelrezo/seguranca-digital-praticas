# A17 — OpenVPN e máquina interna na VPC

Duas EC2 na **mesma VPC**, lançadas pelo **console AWS Academy**: gateway público e máquina interna sem IP público/Internet. Cliente OpenVPN nativo Windows ou Linux. Siga a [aula completa](https://rafaelrezo.github.io/seguranca-digital/aulas/A17-openvpn-ec2/), incluindo preparação da rede, rotas, filtros e encerramento. Nenhum script cria recursos AWS.

## Rede de referência

| Componente | Configuração |
|---|---|
| VPC | 10.77.0.0/16, sem IPv6 |
| Gateway | Pública 10.77.1.0/24, privado 10.77.1.10, IPv4 público automático |
| Interna | Privada 10.77.2.0/24, privado 10.77.2.10, sem IPv4 público |
| VPN | 10.8.0.0/24, tun0 do gateway 10.8.0.1 |

Não use esses endereços se houver sobreposição com sua rede/VPN. Não crie NAT/Elastic IP. Na tabela pública: local e 0.0.0.0/0 → Internet Gateway. Na privada: local e **10.8.0.0/24 → ENI do gateway**, sem saída padrão. Desative **source/destination check somente no gateway**.

SG gateway: TCP22 e UDP1194 somente do IPv4 público da dupla /32; saída IPv4 padrão. SG interna: TCP22/8080 do **CIDR 10.8.0.0/24**, sem regras de saída iniciada; respostas são stateful. O encaminhamento Linux limita destino/portas, sem NAT.

## Máquina interna: preparar sem Internet

No lançamento da **interna Ubuntu 24.04**, informe IPv4 privado 10.77.2.10 e, em **Advanced details → User data → Choose file**, selecione `interna-user-data.sh`. Use a mesma chave SSH descartável do gateway.

O script usa Python já presente na AMI, sem apt/downloads. Cria serviço systemd `a17-http`, usuário sem privilégio, escuta **10.77.2.10:8080**. A máquina interna não executa OpenVPN. `servico.sh` é um aviso de compatibilidade da edição anterior; não inicia HTTP no gateway.

## PKI local e gateway

Com ambiente Python ativo, em `~/seguranca-digital-praticas/a17`:

```bash
python3 pki_a17.py iniciar
```

Guarde a chave SSH como `acesso-a17.pem`, permissão 600. A aula explica o SCP dos scripts e materiais. **CA e privada do cliente ficam locais**, sem envio ao gateway. Recupere `ta.key` por SSH e gere `python3 pki_a17.py perfil "$IP_EC2"`.

No **gateway EC2**, em `~/a17`, use uma etapa por vez:

```bash
bash servidor.sh preparar
bash servidor.sh configurar
bash roteamento.sh aplicar
bash servidor.sh iniciar
```

`preparar` instala pacotes e gera/preserva `ta.key`; `configurar` instala os arquivos recebidos. `roteamento.sh aplicar` habilita forwarding com filtro TCP22/8080 somente para 10.77.2.10. `iniciar` ocupa o terminal com OpenVPN. Em outro SSH, `bash roteamento.sh inspecionar` mostra rotas, forwarding e contadores. Reaplique após reboot. Não execute esses scripts no notebook.

## Cliente e verificações

Antes de conectar, execute o verificador e registre **V0**, sem resposta HTTP. **Linux nativo:** `bash cliente_linux.sh original`; em outro terminal, `bash verificar_linux.sh`.

**Windows:** importe `cliente-a17.ovpn` no OpenVPN GUI e execute `verificar_windows.cmd` no Windows, não no WSL. Localize a rota **10.77.2.0/24** e a frase **A17: maquina interna sem Internet**. Isso é **V1**: acesso ao serviço da segunda EC2. Para SSH, use o cliente nativo no mesmo sistema da VPN e a chave EC2, destino `ubuntu@10.77.2.10`.

Na interna, confira `systemctl is-active a17-http` e `sudo journalctl -u a17-http --no-pager -n 15`: o pedido deve ter origem **10.8.0.x**, preservada sem NAT. A aula inclui tentativa externa curta e conferência de IP/SG/rotas para validar ausência de Internet. O túnel protege até o gateway; HTTP depois dele está em claro. SSH protege até o destino.

**V2:** desconecte, gere `python3 pki_a17.py perfil-errado`, importe/use `cliente-nome-errado.ovpn` e confira recusa de nome; no Linux, `bash cliente_linux.sh nome-errado`. Restaure o original e valide V1.

**V3:** feche SSH da interna, desconecte, execute `python3 pki_a17.py revogar`; envie somente a CRL atualizada, use `bash servidor.sh atualizar-crl` e reinicie o servidor descartável antes da nova conexão com o perfil original. Confira recusa por revogação no log do servidor. Não é expulsão imediata automática de sessão existente.

Termine **as duas EC2**, confira dois EBS/ENIs e remova somente a rede dedicada da dupla, conforme a aula. Não publique perfis, privadas, certificados gerados, IP público ou logs brutos.
