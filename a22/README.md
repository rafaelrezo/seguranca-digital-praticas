# A22 — prática local de superfície e identidade

Use esta pasta junto com a [página da A22](https://rafaelrezo.github.io/seguranca-digital/aulas/A22-pentest-superficie-e-identidade/). A página define perguntas, interpretação e registro; aqui estão os arquivos prontos. Execute apenas em `127.0.0.1`.

## Preparação

```bash
git clone https://github.com/rafaelrezo/seguranca-digital-praticas.git
cd seguranca-digital-praticas/a22
python3 servidor_ordens_a22.py
```

Deixe o servidor aberto. Em outro terminal, entre na mesma pasta. A porta 3001 deve responder a `curl -i http://127.0.0.1:3001/`; `Ctrl+C` encerra. O servidor usa somente a biblioteca padrão do Python. `nmap`, `ffuf` e ZAP são usados nos passos correspondentes da página; não há instalação obrigatória para acompanhar a análise das saídas.

## Arquivos

| Arquivo | Função |
|---|---|
| `servidor_ordens_a22.py` | API fictícia em loopback, duas contas e uma falha de leitura intencional para comparar autorização no Requester |
| `palavras_a22.txt` | Lista curta para calibrar `ffuf` sem varredura extensa |
| `ler_jwt.py` | Decodifica um JWT, sem validar a assinatura |
| `servidor_jwt.py` | Emite, adultera e verifica tokens fictícios localmente |

As contas descartáveis são `u1@lab.invalid` / `senha-u1` e `u2@lab.invalid` / `senha-u2`. O servidor de ordens usa tokens **opacos** (`lab-u1`, `lab-u2`); o ensaio de JWT é um programa separado. Nenhum dado ou resposta do Juice Shop integra esta pasta.

Não publique tokens reais ou capturas sem mascarar credenciais. Reiniciar o servidor recompõe as duas sessões fictícias e as ordens 17 e 18. A aplicação local não implementa escrita de ordens.
