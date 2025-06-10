from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from vdf import generate_rsa_keys, repeated_squaring, encrypt_with_vdf_key, decrypt_with_vdf_key
from ..models.models import Product, Bid
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import hashlib
import base64
import os

def test_vdf_auction_flow(db: Session):
    # Criar RSA
    private_key, private_pem, public_pem = generate_rsa_keys()

    # VDF setup
    secret = os.urandom(32)
    difficulty = 5000  # usar valor pequeno no teste
    modulus = int.from_bytes(os.urandom(256), "big")  # VDF modulus
    vdf_key = hashlib.sha256(secret).digest()
    encrypted_private_key = encrypt_with_vdf_key(vdf_key, private_pem)

    # Simular criação do produto
    product = Product(
        name="Test VDF Product",
        description="Produto de teste com VDF",
        base_value=100,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(seconds=5),
        seller_id=1,
        rsa_public_key=public_pem,
        rsa_private_key_encrypted=encrypted_private_key,
        vdf_secret=base64.b64encode(secret).decode(),
        vdf_modulus=str(modulus),
        vdf_difficulty=difficulty
    )
    db.add(product)
    db.commit()

    # Simular bid
    bid_value = 200
    salt = os.urandom(16).hex()
    commitment_hash = hashlib.sha256(f"{bid_value}{salt}".encode()).hexdigest()

    # Encriptar com chave pública
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    import base64

    public_key = serialization.load_pem_public_key(product.rsa_public_key.encode())
    encrypted_value = public_key.encrypt(
        str(bid_value).encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted_value_b64 = base64.b64encode(encrypted_value).decode()

    bid = Bid(
        user_id=2,
        product_id=product.id,
        encrypted_value=encrypted_value_b64,
        salt=salt,
        commitment_hash=commitment_hash,
        time_stamp=datetime.utcnow()
    )
    db.add(bid)
    db.commit()

    print("✅ Produto e bid criados.")

    # Simular o final do leilão (resolve VDF)
    print("⏳ A resolver VDF...")
    vdf_output = repeated_squaring(base64.b64decode(product.vdf_secret), difficulty, modulus)
    vdf_derived_key = hashlib.sha256(str(vdf_output).encode()).digest()
    decrypted_pem = decrypt_with_vdf_key(vdf_derived_key, product.rsa_private_key_encrypted)
    private_key = serialization.load_pem_private_key(decrypted_pem.encode(), password=None)

    # Desencriptar bid
    decrypted_bid_bytes = private_key.decrypt(
        base64.b64decode(bid.encrypted_value),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    decrypted_value = int(decrypted_bid_bytes.decode())
    print(f"🔓 Valor desencriptado: {decrypted_value}")

    assert decrypted_value == bid_value, "❌ Valor desencriptado não corresponde"
    print("✅ Teste VDF concluído com sucesso")
