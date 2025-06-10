import base64
import hashlib
import secrets
import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.fernet import Fernet

from chiavdf import create_discriminant, prove

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.test_models import Product, Bid, User
from app.db.test_base import TestBase
from app.crud.product import finalize_expired_auctions


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestBase.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_finalize_expired_with_real_vdf(db_session):
    # Criar utilizadores
    seller = User(id=1, name="Vendedor", email="vendedor@mail.com", password="1234")
    bidder = User(id=42, name="Comprador", email="comprador@mail.com", password="1234")
    db_session.add_all([seller, bidder])
    db_session.commit()

    # 1. Gerar chave RSA
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 2. Gerar VDF real
    challenge = secrets.token_bytes(32)
    iterations = 50000
    # Remove o prefixo '-0x' e converte para bytes
    discriminant_str = create_discriminant(challenge, 2048)
    discriminant_hex = discriminant_str[3:]  # remove "-0x"
    discriminant_bytes = int(discriminant_hex, 16).to_bytes((len(discriminant_hex) + 1) // 2, byteorder='big')


    output, proof = prove(discriminant_bytes, challenge, iterations)

    # 3. Encriptar chave privada
    key = hashlib.sha256(output).digest()
    fernet_key = base64.urlsafe_b64encode(key[:32])
    fernet = Fernet(fernet_key)
    encrypted_private_key = fernet.encrypt(private_pem)

    now = datetime.now(tz=ZoneInfo("UTC"))

    # 4. Criar produto expirado
    product = Product(
        name="Produto com VDF",
        description="Teste com VDF real",
        base_value=100,
        start_date=now - timedelta(hours=1),
        end_date=now - timedelta(minutes=1),
        seller_id=1,
        winner_id=None,
        product_type_id=1,  # garantir que o tipo existe se necessário
        rsa_public_key=public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode(),
        rsa_private_key_encrypted=encrypted_private_key.decode(),
        vdf_challenge=base64.b64encode(challenge).decode(),
        vdf_discriminant=str(discriminant),
        vdf_output=output.hex(),
        vdf_proof=proof.hex(),
        vdf_iterations=iterations,
        vdf_start_time=now - timedelta(hours=1)
    )
    db_session.add(product)
    db_session.commit()

    # 5. Criar bid
    bid_value = 150
    salt = "abc123"
    plaintext = str(bid_value).encode()

    encrypted_value = base64.b64encode(
        public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    ).decode()

    commitment_hash = hashlib.sha256(f"{bid_value}{salt}".encode()).hexdigest()

    bid = Bid(
        product_id=product.id,
        user_id=42,
        encrypted_value=encrypted_value,
        commitment_hash=commitment_hash,
        salt=salt,
        time_stamp=datetime.now()
    )
    db_session.add(bid)
    db_session.commit()

    # 6. Finalizar leilões expirados
    finalize_expired_auctions(db_session)

    # 7. Verificar resultado
    updated_product = db_session.get(Product, product.id)
    assert updated_product.winner_id == 42, "O vencedor não foi corretamente atribuído"
