"""A15: ECDSA numérico didático e comparação real RSA-PSS/ECDSA.

Etapa 1 usa parâmetros minúsculos para explicar a matemática, sem segurança.
Etapa 2 usa cryptography; as privadas reais não são impressas nem gravadas.
"""

import argparse

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa, utils


def numeros():
    # Curva didática: y² = x³ + 2x + 2 (mod 17); G tem ordem 19.
    # None representa o ponto neutro O. Não é código de produção.
    p_c, a, n_c = 17, 2, 19
    G = (5, 1)

    def somar(P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p_c == 0:
            return None
        if P == Q:
            inclinacao = (3 * x1 * x1 + a) * pow(2 * y1, -1, p_c) % p_c
        else:
            inclinacao = (y2 - y1) * pow(x2 - x1, -1, p_c) % p_c
        x3 = (inclinacao * inclinacao - x1 - x2) % p_c
        y3 = (inclinacao * (x1 - x3) - y1) % p_c
        return x3, y3

    def multiplicar(escalar, ponto):
        resultado = None
        while escalar:
            if escalar & 1:
                resultado = somar(resultado, ponto)
            ponto = somar(ponto, ponto)
            escalar >>= 1
        return resultado

    d, k, z = 7, 3, 11  # todos públicos no exemplo didático; nunca usar em produção
    Q = multiplicar(d, G)
    R = multiplicar(k, G)
    r = R[0] % n_c
    s = pow(k, -1, n_c) * (z + r * d) % n_c

    print('Curva didática: y² = x³ + 2x + 2 (mod 17); ordem de G: 19')
    print('G:', G, '| 2G:', multiplicar(2, G), '| 3G:', multiplicar(3, G))
    print('19G é O?', multiplicar(n_c, G) is None)
    print('Privada didática d:', d, '| pública Q = dG:', Q)
    print('z fornecido:', z, '| k didático:', k, '| R = kG:', R)
    print('Assinatura didática (r, s):', (r, s))
    for resumo in (11, 12):
        w = pow(s, -1, n_c)
        u1, u2 = resumo * w % n_c, r * w % n_c
        X = somar(multiplicar(u1, G), multiplicar(u2, Q))
        aceita = X is not None and X[0] % n_c == r
        print(f'z={resumo}: w={w}, u1={u1}, u2={u2}, X={X}; aceita? {aceita}')
    print('z=11/12 são números fornecidos; este bloco não calcula hash de mensagem.')


def assinaturas():
    original = b'relatorio=7;resultado=aprovado'
    alterado = b'relatorio=7;resultado=recusado'
    privada_rsa = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    privada_ec = ec.generate_private_key(ec.SECP256R1())
    pss = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32)
    assinatura_rsa = privada_rsa.sign(original, pss, hashes.SHA256())
    assinatura_ec = privada_ec.sign(original, ec.ECDSA(hashes.SHA256()))

    def verificar_rsa(dados):
        privada_rsa.public_key().verify(assinatura_rsa, dados, pss, hashes.SHA256())

    def verificar_ec(dados):
        privada_ec.public_key().verify(assinatura_ec, dados, ec.ECDSA(hashes.SHA256()))

    print('Mesmo conteúdo e SHA-256; pares separados para cada algoritmo.')
    print('RSA-PSS: módulo 3072 bits; assinatura:', len(assinatura_rsa), 'bytes')
    print('ECDSA: P-256; assinatura DER nesta execução:', len(assinatura_ec), 'bytes')
    r, s = utils.decode_dss_signature(assinatura_ec)
    par_fixo = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
    print('ECDSA: o par (r,s) em largura fixa tem', len(par_fixo), 'bytes; DER é outra codificação.')
    for nome, verificar in (('RSA-PSS', verificar_rsa), ('ECDSA', verificar_ec)):
        for rotulo, dados in (('original', original), ('alterado', alterado)):
            try:
                verificar(dados)
                print(nome, rotulo + ': aceita')
            except InvalidSignature:
                print(nome, rotulo + ': recusada')
    print('Não é benchmark. Privadas não foram impressas nem salvas.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--etapa', type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    if args.etapa == 1:
        numeros()
    else:
        assinaturas()
