# app/utils/crypto.py

import logging
import base64

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet


logger = logging.getLogger("LS")

def generate_rsa_keys():
    """Generate RSA key and export in PEM format (private and public)"""
    
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    return private_pem, public_pem

def encrypt_with_vdf_key(key_bytes: bytes, plaintext_bytes: bytes) -> str:
    """Use VDF key (hash) to encrypt PEM with Fernet"""
    if len(key_bytes) < 32:
        raise ValueError("key_bytes must have at least 32 bytes.")
    key = base64.urlsafe_b64encode(key_bytes[:32])
    f = Fernet(key)
    return f.encrypt(plaintext_bytes).decode()

def decrypt_with_vdf_key(key_bytes: bytes, ciphertext: str) -> str:
    """Desencripta PEM com chave derivada da VDF"""
    if len(key_bytes) < 32:
        raise ValueError("key_bytes must have at least 32 bytes.")
    try:
        key = base64.urlsafe_b64encode(key_bytes[:32])
        f = Fernet(key)
        decrypted_bytes = f.decrypt(ciphertext.encode())
        return decrypted_bytes.decode()
    except Exception as e:
        logger.error(f"Error decrypting with VDF key", exc_info=True)
        raise
