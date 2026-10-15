"""PKI descartável da A17. Executar localmente, nunca na EC2.

Uso: python3 pki_a17.py iniciar | perfil IPV4 | perfil-errado | revogar
Depende da biblioteca cryptography já usada na A14.
"""

import argparse
from datetime import datetime, timedelta, timezone
from getpass import getpass
from ipaddress import IPv4Address
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

PASTA = Path("pki")


def salvar(nome, dados, privado=False):
    destino = PASTA / nome
    destino.write_bytes(dados)
    destino.chmod(0o600 if privado else 0o644)


def certificado(nome, chave, emissor, chave_emissora, ca=False, uso=None):
    agora = datetime.now(timezone.utc)
    sujeito = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, nome)])
    builder = (
        x509.CertificateBuilder()
        .subject_name(sujeito)
        .issuer_name(emissor or sujeito)
        .public_key(chave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(agora - timedelta(minutes=5))
        .not_valid_after(agora + timedelta(days=2))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=0 if ca else None), True)
        .add_extension(x509.KeyUsage(
            digital_signature=True, content_commitment=False,
            key_encipherment=False, data_encipherment=False, key_agreement=False,
            key_cert_sign=ca, crl_sign=ca, encipher_only=False, decipher_only=False,
        ), True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(chave.public_key()), False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(
            chave_emissora.public_key()
        ), False)
    )
    if uso is not None:
        builder = builder.add_extension(x509.ExtendedKeyUsage([uso]), False)
    return builder.sign(chave_emissora, hashes.SHA256())


def gravar_crl(chave_ca, cert_ca, revogado=None):
    agora = datetime.now(timezone.utc)
    builder = (
        x509.CertificateRevocationListBuilder()
        .issuer_name(cert_ca.subject)
        .last_update(agora - timedelta(minutes=1))
        .next_update(agora + timedelta(days=2))
    )
    if revogado is not None:
        entrada = (x509.RevokedCertificateBuilder()
                   .serial_number(revogado.serial_number)
                   .revocation_date(agora)
                   .build())
        builder = builder.add_revoked_certificate(entrada)
    crl = builder.sign(chave_ca, hashes.SHA256())
    salvar("crl.pem", crl.public_bytes(serialization.Encoding.PEM))


def iniciar():
    if PASTA.exists():
        raise ValueError("A pasta pki já existe. Preserve-a; use uma nova pasta de trabalho para outro ensaio.")
    frase = getpass("Frase descartável para proteger CA e chave do cliente: ")
    if not frase or frase != getpass("Repita a frase: "):
        raise ValueError("Frases vazias ou diferentes; nada foi criado.")
    PASTA.mkdir(mode=0o700)
    protecao = serialization.BestAvailableEncryption(frase.encode("utf-8"))
    chave_ca = ec.generate_private_key(ec.SECP256R1())
    cert_ca = certificado("CA-Lab-A17", chave_ca, None, chave_ca, ca=True)
    salvar("ca.key", chave_ca.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, protecao
    ), True)
    salvar("ca.crt", cert_ca.public_bytes(serialization.Encoding.PEM))
    for arquivo, nome, uso in (
        ("servidor", "vpn-a17", ExtendedKeyUsageOID.SERVER_AUTH),
        ("cliente", "dupla-a17", ExtendedKeyUsageOID.CLIENT_AUTH),
    ):
        chave = ec.generate_private_key(ec.SECP256R1())
        cert = certificado(nome, chave, cert_ca.subject, chave_ca, uso=uso)
        # O servidor inicia sem prompt; sua privada depende de permissão e acesso SSH.
        cifra = protecao if arquivo == "cliente" else serialization.NoEncryption()
        salvar(arquivo + ".key", chave.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, cifra
        ), True)
        salvar(arquivo + ".crt", cert.public_bytes(serialization.Encoding.PEM))
    gravar_crl(chave_ca, cert_ca)
    print("PKI local criada: CA, servidor, cliente e CRL vazia; prazo de dois dias.")
    print("A privada da CA e a privada do cliente permanecem locais.")


def perfil(ip):
    endereco = str(IPv4Address(ip))
    destino = Path("cliente-a17.ovpn")
    if destino.exists():
        raise ValueError("cliente-a17.ovpn já existe; preserve o perfil ou use outra pasta de trabalho.")
    texto = f"""client
dev tun
proto udp
remote {endereco} 1194
nobind
remote-cert-tls server
verify-x509-name vpn-a17 name
tls-version-min 1.3
tls-groups X25519:prime256v1
data-ciphers AES-256-GCM
auth SHA256
key-direction 1
disable-dco
verb 3
"""
    for tag, arquivo in (("ca", "ca.crt"), ("cert", "cliente.crt"),
                         ("key", "cliente.key"), ("tls-auth", "ta.key")):
        texto += f"<{tag}>\n{(PASTA / arquivo).read_text().strip()}\n</{tag}>\n"
    destino.write_text(texto)
    destino.chmod(0o600)
    print("Perfil cliente-a17.ovpn criado; contém chave privada cifrada. Não publicar.")


def revogar():
    frase = getpass("Frase da CA local: ")
    chave_ca = serialization.load_pem_private_key(
        (PASTA / "ca.key").read_bytes(), frase.encode("utf-8")
    )
    cert_ca = x509.load_pem_x509_certificate((PASTA / "ca.crt").read_bytes())
    cliente = x509.load_pem_x509_certificate((PASTA / "cliente.crt").read_bytes())
    gravar_crl(chave_ca, cert_ca, cliente)
    print("CRL atualizada com o certificado do cliente revogado. Transfira crl.pem ao servidor.")


def perfil_errado():
    original = Path("cliente-a17.ovpn").read_text()
    esperado = "verify-x509-name vpn-a17 name"
    if original.count(esperado) != 1:
        raise ValueError("Perfil original sem identidade única vpn-a17; confira antes de modificar.")
    destino = Path("cliente-nome-errado.ovpn")
    if destino.exists():
        raise ValueError("O perfil de contraprova já existe; preserve-o para comparação.")
    destino.write_text(original.replace(esperado, "verify-x509-name outro-servidor name"))
    destino.chmod(0o600)
    print("Perfil de contraprova criado: mudou somente o nome esperado.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao", choices=("iniciar", "perfil", "perfil-errado", "revogar"))
    parser.add_argument("ipv4", nargs="?")
    args = parser.parse_args()
    try:
        if args.acao == "iniciar":
            iniciar()
        elif args.acao == "perfil":
            if not args.ipv4:
                parser.error("perfil exige o IPv4 público da sua EC2")
            perfil(args.ipv4)
        elif args.acao == "perfil-errado":
            perfil_errado()
        else:
            revogar()
    except (ValueError, OSError) as erro:
        parser.exit(1, f"Parada: {erro}\n")


if __name__ == "__main__":
    main()
