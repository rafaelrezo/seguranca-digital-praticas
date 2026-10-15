import argparse

parser = argparse.ArgumentParser(description='A14: executar até a etapa indicada, sem montar o código.')
parser.add_argument('--etapa', type=int, choices=(1, 2, 3, 4), default=3)
args = parser.parse_args()

from hashlib import pbkdf2_hmac
from os import urandom
from pathlib import Path
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# 1. Emissor: derivar a chave, cifrar e mostrar os valores
senha_emissor = b'senha-descartavel-a14'  # segredo fictício já conhecido nos dois lados
iterations = 100_000               # custo didático; não é recomendação de produção
salt = urandom(16)
key = pbkdf2_hmac('sha256', senha_emissor, salt, iterations, dklen=32)
nonce = urandom(12)
aad = b'tipo=transferencia;versao=1'
text = b'{"origem":"conta123","destino":"conta456","valor":5000}'
sealed = AESGCM(key).encrypt(nonce, text, aad)

print("Salt:  ", salt.hex())
print("Key:   ", key.hex())
print("Nonce: ", nonce.hex())
print("AAD:   ", aad.hex())
print("Text:  ", text.hex())
print("Sealed:", sealed.hex())

print("\nRepresentação textual:")
print("AAD:   ", aad.decode("utf-8"))
print("Text:  ", text.decode("utf-8"))

print("\nComponentes AES-GCM:")
print("Ciphertext:", sealed[:-16].hex())
print("Tag:       ", sealed[-16:].hex())

if args.etapa == 1:
    raise SystemExit(0)

# 2. Envelope: gravar apenas os campos públicos, depois ler como receptor
packet = {
    'salt': salt.hex(),
    'nonce': nonce.hex(),
    'aad': aad.decode('utf-8'),
    'ciphertext': sealed[:-16].hex(),
    'tag': sealed[-16:].hex(),
}
file = Path('mensagem_gcm.json')
file.write_text(json.dumps(packet, indent=2), encoding='utf-8')
print('\nEnvelope gravado em:', file)

received = json.loads(file.read_text(encoding='utf-8'))
senha_receptor = b'senha-descartavel-a14'  # já conhecida; não vem do envelope
receiver_key = pbkdf2_hmac(
    'sha256', senha_receptor, bytes.fromhex(received['salt']), iterations, dklen=32
)
receiver_nonce = bytes.fromhex(received['nonce'])
receiver_aad = received['aad'].encode('utf-8')
receiver_sealed = bytes.fromhex(received['ciphertext']) + bytes.fromhex(received['tag'])

print('G1 chaves iguais:', key == receiver_key)
print('G1 tag:', received['tag'])
print('G1 texto:', AESGCM(receiver_key).decrypt(
    receiver_nonce, receiver_sealed, receiver_aad
).decode('utf-8'))

if args.etapa == 2:
    raise SystemExit(0)

# 3. Contraprovas: alterar tag ou AAD do conjunto recebido
tampered = receiver_sealed[:-1] + bytes([receiver_sealed[-1] ^ 1])
print('G2 tag:', tampered[-16:].hex())
try:
    AESGCM(receiver_key).decrypt(receiver_nonce, tampered, receiver_aad)
    print('G2: aceito (inesperado)')
except InvalidTag:
    print('G2: rejeitado; texto não entregue')

altered_aad = b'tipo=transferencia;versao=2'
try:
    AESGCM(receiver_key).decrypt(receiver_nonce, receiver_sealed, altered_aad)
    print('G3: aceito (inesperado)')
except InvalidTag:
    print('G3: rejeitado; AAD alterado')

if args.etapa == 3:
    raise SystemExit(0)

# 4. Extensões: novo nonce, repetição do envelope e senha diferente
nonce2 = urandom(12)
while nonce2 == nonce:
    nonce2 = urandom(12)
sealed2 = AESGCM(key).encrypt(nonce2, text, aad)
print('G4 nonce 1:', nonce.hex())
print('G4 nonce 2:', nonce2.hex())
print('G4 mesmo texto, ciphertext diferente?', sealed[:-16] != sealed2[:-16])

print('G5 envelope repetido:', AESGCM(receiver_key).decrypt(
    receiver_nonce, receiver_sealed, receiver_aad
).decode('utf-8'))

wrong_key = pbkdf2_hmac('sha256', b'outra-senha', salt, iterations, dklen=32)
try:
    AESGCM(wrong_key).decrypt(receiver_nonce, receiver_sealed, receiver_aad)
    print('G6: aceito (inesperado)')
except InvalidTag:
    print('G6: rejeitado; senha diferente gera outra chave')
