"""Papel do servidor em um JWT HS256 — CECA067 (laboratório local).

O servidor guarda uma chave HMAC que o cliente não conhece (A16). Ele emite
tokens e, a cada requisição, recalcula a assinatura antes de confiar no payload.

Uso:
    python3 servidor_jwt.py emitir  <email> <papel>  > meu.jwt
    python3 servidor_jwt.py verificar meu.jwt
    python3 servidor_jwt.py adulterar meu.jwt <novo-papel> > adulterado.jwt
"""
import base64
import hashlib
import hmac
import json
import sys
import time

# Chave fictícia do laboratório. Em um sistema real ela fica no servidor,
# fora do código-fonte, e nunca é enviada ao navegador.
CHAVE_DO_SERVIDOR = b"chave-ficticia-do-laboratorio-ceca067"


def b64url(dados: bytes) -> str:
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode()


def de_b64url(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def assinar(cabecalho_payload: str) -> str:
    return b64url(hmac.new(CHAVE_DO_SERVIDOR, cabecalho_payload.encode(), hashlib.sha256).digest())


def emitir(email, papel):
    agora = int(time.time())
    cabecalho = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = b64url(json.dumps({"sub": email, "papel": papel, "iat": agora, "exp": agora + 3600},
                                separators=(",", ":")).encode())
    print(f"{cabecalho}.{payload}.{assinar(cabecalho + '.' + payload)}")


def verificar(caminho):
    cabecalho, payload, assinatura = open(caminho, encoding="utf-8").read().strip().split(".")
    if json.loads(de_b64url(cabecalho)).get("alg") != "HS256":
        print("RECUSADO: algoritmo diferente do esperado pelo servidor")
        return
    esperada = assinar(cabecalho + "." + payload)
    if not hmac.compare_digest(esperada, assinatura):
        print("RECUSADO: assinatura não confere")
        return
    dados = json.loads(de_b64url(payload))
    if dados["exp"] < time.time():
        print("RECUSADO: token expirado")
        return
    print(f"ACEITO: sub={dados['sub']} papel={dados['papel']}")


def adulterar(caminho, novo_papel):
    cabecalho, payload, assinatura = open(caminho, encoding="utf-8").read().strip().split(".")
    dados = json.loads(de_b64url(payload))
    dados["papel"] = novo_papel
    novo = b64url(json.dumps(dados, separators=(",", ":")).encode())
    # O cliente consegue trocar o payload, mas não consegue recalcular a assinatura.
    print(f"{cabecalho}.{novo}.{assinatura}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "emitir" and len(sys.argv) == 4:
        emitir(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "verificar":
        verificar(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "adulterar":
        adulterar(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(2)
