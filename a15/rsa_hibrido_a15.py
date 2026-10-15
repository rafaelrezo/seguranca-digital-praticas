import argparse

parser = argparse.ArgumentParser(description='A15: limite OAEP e composição RSA/AES-GCM.')
parser.add_argument('--etapa', type=int, choices=(1, 2), default=2)
args = parser.parse_args()

import json
from os import urandom
from pathlib import Path
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 1. Chaves descartáveis do receptor e teste do limite RSA-OAEP.
privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
publica = privada.public_key()  # pública do receptor, aceita neste ensaio local
oaep = padding.OAEP(
    mgf=padding.MGF1(hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None,
)

curta = b'A' * 190
cifrada_curta = publica.encrypt(curta, oaep)
print('R1 — 190 bytes recuperados?', privada.decrypt(cifrada_curta, oaep) == curta)
print('R1 — tamanho cifrado RSA:', len(cifrada_curta), 'bytes')
try:
    publica.encrypt(b'A' * 191, oaep)
    print('R2 — 191 bytes aceitos (inesperado)')
except ValueError:
    print('R2 — 191 bytes rejeitados: ultrapassam o limite de 190')

if args.etapa == 1:
    raise SystemExit(0)

# 2. Emissor: AES-GCM protege o texto; RSA-OAEP protege somente a chave AES.
key = AESGCM.generate_key(bit_length=256)
nonce = urandom(12)
aad = b'tipo=relatorio;versao=1'
text = ('Relatorio de seguranca.\n' * 200).encode('utf-8')
sealed = AESGCM(key).encrypt(nonce, text, aad)
chave_cifrada = publica.encrypt(key, oaep)

print('\nKey AES descartável:', key.hex())
print('Nonce:', nonce.hex())
print('AAD:', aad.decode('utf-8'))
print('Tag:', sealed[-16:].hex())
print('Texto:', len(text), 'bytes | Ciphertext:', len(sealed[:-16]), 'bytes')
print('H1 — chave AES:', len(key), 'bytes | chave cifrada RSA:', len(chave_cifrada), 'bytes')

pacote = {
    'chave_cifrada': chave_cifrada.hex(),
    'nonce': nonce.hex(),
    'aad': aad.decode('utf-8'),
    'ciphertext': sealed[:-16].hex(),
    'tag': sealed[-16:].hex(),
}
arquivo = Path('envelope_rsa_aes.json')
arquivo.write_text(json.dumps(pacote, indent=2), encoding='utf-8')

# 3. Receptor: recuperar K pelo RSA e verificar/abrir o texto com AES-GCM.
recebido = json.loads(arquivo.read_text(encoding='utf-8'))
key_receptor = privada.decrypt(bytes.fromhex(recebido['chave_cifrada']), oaep)
nonce_receptor = bytes.fromhex(recebido['nonce'])
aad_receptor = recebido['aad'].encode('utf-8')
sealed_receptor = bytes.fromhex(recebido['ciphertext']) + bytes.fromhex(recebido['tag'])
texto_aberto = AESGCM(key_receptor).decrypt(nonce_receptor, sealed_receptor, aad_receptor)
print('H2 — texto longo recuperado?', texto_aberto == text)
print('H2 — início do texto:', texto_aberto[:46].decode('utf-8'))

# 4. Contraprova: alterar somente um bit da tag recebida.
alterado = sealed_receptor[:-1] + bytes([sealed_receptor[-1] ^ 1])
try:
    AESGCM(key_receptor).decrypt(nonce_receptor, alterado, aad_receptor)
    print('H3 — tag alterada aceita (inesperado)')
except InvalidTag:
    print('H3 — tag alterada rejeitada; texto não entregue')
