# A16 — hash, HMAC, senhas e TLS

Entre em `~/seguranca-digital-praticas/a16` com o ambiente Python ativo. Os arquivos de entrada já têm os bytes exatos da [A16](https://rafaelrezo.github.io/seguranca-digital/aulas/A16-tls-ciclo-de-chaves/), sem quebra de linha:

```bash
bash hash_hmac.sh hash
bash hash_hmac.sh hmac
bash hash_hmac.sh mensagem-alterada
bash hash_hmac.sh chave-alterada
python3 verificador_senhas_a16.py
python3 verificador_senhas_a16.py --repetir-sal
```

`--repetir-sal` executa S4 sem editar o programa. Não é configuração de armazenamento de senhas.

TLS precisa dos certificados válidos emitidos em `../a15`. Em um terminal:

```bash
bash tls.sh servidor
```

Em outro terminal do **mesmo Linux/WSL**, entre em `a16` e execute separadamente:

```bash
bash tls.sh handshake
bash tls.sh nome-errado
bash tls.sh http
```

O servidor escuta apenas em 127.0.0.1:8443. Encerre-o com `Ctrl+C` no primeiro terminal. Consulta externa opcional: `bash tls.sh publico` verifica o domínio HTTPS do curso; não é requisito do teste local.
