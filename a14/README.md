# A14 — cifra simétrica

Entre na pasta, com o ambiente Python ativo:

```bash
cd ~/seguranca-digital-praticas/a14
bash cbc.sh preparar
bash cbc.sh cifrar
bash cbc.sh inspecionar
bash cbc.sh abrir
```

Use uma senha descartável; na abertura, digite a mesma senha. `claro.txt` já contém os bytes da aula. Cada comando corresponde a uma pausa de observação; CBC não verifica tag.

No GCM, execute **até** a etapa que a aula está explicando:

```bash
python3 aes_gcm_a14.py --etapa 1
python3 aes_gcm_a14.py --etapa 2
python3 aes_gcm_a14.py --etapa 3
```

1 mostra entradas/cifra; 2 inclui envelope e receptor; 3 inclui rejeição da tag e do AAD alterados. Cada execução gera novos valores: compare dentro da mesma execução. O padrão sem opção termina na etapa 3.

Extensão opcional:

```bash
python3 aes_gcm_a14.py --etapa 4
```

G4 usa outro nonce; G5 abre novamente o mesmo envelope; G6 rejeita outra senha. Leia os resultados e limites na [A14](https://rafaelrezo.github.io/seguranca-digital/aulas/A14-cifra-simetrica-autenticada/). Não entregue a senha ou a chave impressa.
