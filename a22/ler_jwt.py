"""Decodifica cabeçalho e payload de um JWT, sem verificar a assinatura — CECA067.

Uso:
    python3 ler_jwt.py arquivo-com-o-jwt.txt

Guarde o JWT em um arquivo (sem a palavra Bearer) para não deixá-lo no
histórico do terminal. Decodificar NÃO prova que o token é autêntico.
"""
import base64
import datetime
import json
import sys


def b64url(parte):
    parte += "=" * (-len(parte) % 4)
    return base64.urlsafe_b64decode(parte)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    jwt_texto = open(sys.argv[1], encoding="utf-8").read().strip()
    partes = jwt_texto.split(".")
    if len(partes) != 3:
        print(f"Esperava 3 partes separadas por ponto; encontrei {len(partes)}.")
        sys.exit(1)
    for nome, parte in zip(("CABEÇALHO", "PAYLOAD"), partes[:2]):
        dados = json.loads(b64url(parte))
        print(f"\n{nome}:")
        print(json.dumps(dados, indent=2, ensure_ascii=False))
        for campo in ("iat", "nbf", "exp"):
            if campo in dados:
                instante = datetime.datetime.fromtimestamp(dados[campo], datetime.timezone.utc)
                print(f"  {campo} = {instante:%Y-%m-%d %H:%M:%S} UTC")
    print(f"\nASSINATURA: {len(b64url(partes[2]))} bytes (não verificada por este programa)")


if __name__ == "__main__":
    main()
