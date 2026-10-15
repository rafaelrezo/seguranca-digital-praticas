# A15 — chaves, assinaturas e certificados

Entre em `~/seguranca-digital-praticas/a15` com o ambiente Python ativo. Execute um comando por etapa da [A15](https://rafaelrezo.github.io/seguranca-digital/aulas/A15-chaves-assinaturas-certificados/):

```bash
bash chaves.sh
python3 rsa_numeros_a15.py --etapa 1
python3 rsa_numeros_a15.py --etapa 2
python3 rsa_hibrido_a15.py --etapa 1
python3 rsa_hibrido_a15.py --etapa 2
bash assinatura.sh original
bash assinatura.sh alterado
bash assinatura.sh outra-chave
bash certificados.sh emitir
bash certificados.sh inspecionar
bash certificados.sh verificar
bash certificados.sh nome-errado
bash certificados.sh sem-ca
```

Os textos `relatorio.txt`, `alterado.txt` e as extensões `servidor-a15.ext` já estão prontos. As privadas são criadas localmente. `chaves.sh` e `certificados.sh emitir` param se as chaves já existirem para não as substituir.

Extensão numérica: `python3 rsa_numeros_a15.py --mensagem 4`; com `--mensagem 55`, a recusa do intervalo é intencional. A fórmula numérica não é RSA de produção.

Preserve `ca-a15.pem`, `servidor-a15.pem` e `servidor-chave-a15.pem` para o TLS da A16. Os certificados expiram em dois dias. Não instale essa CA no sistema nem publique as privadas. Mensagens de recusa esperada aparecem nas contraprovas; erros de arquivo/dependência não comprovam rejeição criptográfica.
