# Segurança Digital — práticas A14–A17

Arquivos prontos para acompanhar as aulas: [material completo do curso](https://rafaelrezo.github.io/seguranca-digital/). Leia a etapa da aula, preveja o resultado e execute o comando indicado. Não é necessário copiar código para montar os programas, criar conta no GitHub ou fazer fork.

## Preparar uma vez

Use Ubuntu/WSL no Windows ou Linux. No Ubuntu/Debian, se faltar alguma ferramenta:

```bash
sudo apt update
sudo apt install git openssl python3-venv
```

Baixe os arquivos pelo terminal:

```bash
cd ~
git clone https://github.com/rafaelrezo/seguranca-digital-praticas.git
cd seguranca-digital-praticas
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Sem Git: use **Code → Download ZIP** no GitHub, extraia e renomeie a pasta para `seguranca-digital-praticas`. Coloque-a na pasta pessoal do Linux/WSL, entre nela e execute as três últimas linhas acima. No WSL, `explorer.exe ~` abre a pasta pessoal para copiar a pasta extraída.

Em cada novo terminal, ative o ambiente antes dos programas Python:

```bash
source ~/seguranca-digital-praticas/.venv/bin/activate
```

Python 3.10 ou posterior, OpenSSL 3 e `cryptography` com versão fixada em `requirements.txt`. Scripts `.sh` usam Bash; abra-os no editor para ler os comandos. No Windows, o cliente VPN da A17 é **OpenVPN GUI nativo**; o WSL prepara certificados e faz SSH/SCP. Não execute os scripts do servidor EC2 na máquina local.

## Abrir a prática

| Pasta | Conteúdo | Primeiro comando, depois de entrar na pasta |
|---|---|---|
| [a14](a14/) | CBC, AES-GCM, envelope e contraprovas | `bash cbc.sh preparar` |
| [a15](a15/) | RSA/OAEP, híbrida, assinatura e certificados | `bash chaves.sh` |
| [a16](a16/) | Hash, HMAC, senhas e TLS local | `bash hash_hmac.sh hash` |
| [a17](a17/) | PKI, configuração EC2 e clientes Windows/Linux | Siga o README e a aula antes de executar. |

Os READMEs de cada pasta listam a ordem dos comandos. Aulas e decisões de aprendizagem permanecem no MkDocs. Os certificados da A15 duram dois dias e são usados pelo TLS da A16; se vencerem, use uma cópia nova da pasta `a15` no mesmo nível de `a16` para reemitir o conjunto.

## Dados e encerramento

Use somente dados fictícios e chaves descartáveis. Os scripts geram arquivos locais; `.gitignore` exclui privadas, certificados, perfis e saídas. Não envie esses arquivos ao GitHub, à IA ou na entrega. O CBC não autentica o arquivo; os parâmetros de senha/custo são didáticos.

Na A17, lance **uma EC2 por dupla pelo console AWS Academy**. O repositório não lança recursos. Conecte o cliente local, valide as recusas e siga o encerramento EC2/EBS descrito na aula; parar o cliente não termina a instância.
