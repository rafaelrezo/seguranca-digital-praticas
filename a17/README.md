# A17 — OpenVPN em EC2

Siga a [A17 completa](https://rafaelrezo.github.io/seguranca-digital/aulas/A17-openvpn-ec2/): lançamento pelo **console EC2**, regras restritas à origem e cliente instalado na **máquina local Windows ou Linux**. Núcleo OpenVPN 2.6+; a aula indica instalador e limites do ensaio.

## Arquivos locais

Na pasta `~/seguranca-digital-praticas/a17`, com o ambiente Python ativo:

```bash
python3 pki_a17.py iniciar
```

Guarde a privada SSH da sua EC2 nessa pasta como `acesso-a17.pem` e use permissão 600. As chaves CA/cliente permanecem locais. A aula orienta transferir os arquivos necessários por SCP, recuperar `ta.key` e executar `python3 pki_a17.py perfil "$IP_EC2"`.

## Scripts para enviar à EC2

- `servidor.sh preparar`: instala pacotes e gera/preserva `ta.key`.
- `servidor.sh configurar`: instala configuração e arquivos recebidos em `/etc/openvpn/server`.
- `servidor.sh iniciar`: inicia o OpenVPN em primeiro plano.
- `servidor.sh atualizar-crl`: verifica e instala a nova CRL; reinicie o servidor de laboratório depois.
- `servico.sh`: inicia HTTP somente em 10.8.0.1:8080; use outro terminal SSH.

Execute com `bash` **na EC2**, em `~/a17`. Nenhum script cria instância, rede ou regra AWS. Não envie `ca.key`, `cliente.key` ou perfis à EC2.

## Cliente local e contraprovas

**Linux nativo:** `bash cliente_linux.sh original`; em outro terminal, `bash verificar_linux.sh`. Para o nome incorreto, use `bash cliente_linux.sh nome-errado`.

**Windows:** importe `cliente-a17.ovpn` no OpenVPN GUI. Copie `verificar_windows.cmd` para uma pasta Windows local junto do perfil e execute pelo Explorer ou Prompt de Comando; os testes precisam ocorrer no Windows que conecta a VPN, não no WSL.

Após V1, desconecte e gere `python3 pki_a17.py perfil-errado`. O arquivo `cliente-nome-errado.ovpn` muda somente a identidade esperada. Importe/use esse perfil para V2 e depois restaure o original. Para V3, `python3 pki_a17.py revogar`, envie somente a CRL atualizada, instale-a e reinicie o servidor descartável antes da nova conexão com o perfil original.

Encerre cliente/processos e **termine a EC2**, conferindo EBS e IPs no console. Não publique `.ovpn`, `.pem`, `.key`, `.crt`, CRL, IP público ou logs brutos. Os arquivos são gerados por você; nenhuma credencial vem neste repositório.
