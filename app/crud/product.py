from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from ..models.models import Bid, Product, User
from fastapi import UploadFile
from typing import List
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64
import hashlib

import os
import shutil

from .user import get_user_by_id

lisbon_tz = ZoneInfo("Europe/Lisbon")


def get_valid_bids_for_product(db: Session, product: Product):
    print("entrou no get_valid_bids_for_product")
    if not product.rsa_private_key_encrypted:
        return []

    private_key = load_pem_private_key(
        product.rsa_private_key_encrypted.encode(),
        password=None
    )

    valid_bids = []
    for bid in product.bids:
        try:
            encrypted_bytes = base64.b64decode(bid.encrypted_value)
            decrypted = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            bid_value = int(decrypted.decode())

            hash_input = f"{bid_value}{bid.salt}".encode()
            expected_commitment = hashlib.sha256(hash_input).hexdigest()

            if expected_commitment == bid.commitment_hash:
                valid_bids.append({
                    "user_id": bid.user_id,
                    "username": get_user_by_id(db, bid.user_id).name,
                    "value": bid_value,
                    "time_stamp": bid.time_stamp
                })
        except Exception:
            continue
    # Ordena primeiro por valor descrescente, depois por time_stamp ascendente
    return sorted(valid_bids, key=lambda x: (-x["value"], x["time_stamp"]))

def get_all_products(db: Session):
    return db.query(Product).all()

def get_product(db: Session, product_id: int):
    return db.get(Product, product_id)

def get_complete_product(db: Session, product_id: int):
    product = db.get(Product, product_id)
    winner = None
    if product.winner_id:
        winner = get_user_by_id(db, product.winner_id)

    # Trazer as licitações associadas
    valid_bids = get_valid_bids_for_product(db, product)
    if valid_bids == []:
        valid_bids.append({
                    "user_id": None,
                    "username": "Nenhum vencedor",
                    "value": 0,
                    "time_stamp": None
                })

    product_data = []
    seller = get_user_by_id(db, product.seller_id)
    product_data.append({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "base_value": product.base_value,
        "start_date": product.start_date,
        "end_date": product.end_date,
        "photos": product.photos or "",
        "seller_name": seller.name if seller else "Desconhecido",
        "winner_name": winner.name if winner else "Sem licitações",
        "bids": valid_bids
    })
    
    return product_data


def get_all_products_with_seller_name(db: Session):
    products = db.query(Product).all()
    product_data = []
    for product in products:
        seller = get_user_by_id(db, product.seller_id)
        product_data.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "base_value": product.base_value,
            "start_date": product.start_date,
            "end_date": product.end_date,
            "photos": product.photos or "",
            "seller_name": seller.name if seller else "Desconhecido"
        })
    
    return product_data

def create_new_product(user_id: any, name: str, description: str, base_value: int, end_dt: datetime, photos: List[UploadFile], db: Session):
    # Gerar par de chaves RSA
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Serializar as chaves
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()  # futuro: encriptar com VDF
    ).decode("utf-8")

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    # Guardar fotos
    photo_paths = []
    os.makedirs("static/product_photos", exist_ok=True)
    for photo in photos:
        if photo.filename:
            filename = f"{datetime.now().timestamp()}_{photo.filename}"
            path = os.path.join("static/product_photos", filename)
            with open(path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            photo_paths.append(f"/static/product_photos/{filename}")

    new_product = Product(
        name=name,
        description=description,
        base_value=base_value,
        start_date=datetime.now().strftime("%d-%m-%Y %H:%M"),
        end_date=end_dt,
        vdf_start_time=None,
        vdf_output=None,
        photos=";".join(photo_paths),  # armazenar como texto separado por ponto e vírgula
        seller_id=user_id,
        winner_id=None,
        product_type_id=None,
        rsa_public_key=public_pem,
        rsa_private_key_encrypted=private_pem
    )
    db.add(new_product)


    
def finalize_expired_auctions(db: Session):
    now = datetime.now()
    products = db.query(Product).filter(
        Product.end_date <= now,
        Product.winner_id == None
    ).all()

    for product in products:
        if not product.rsa_private_key_encrypted:
            continue  # Sem chave para desencriptar

        # TODO: aplicar VDF aqui se for necessário

        # Carregar a chave privada
        private_key = load_pem_private_key(
            product.rsa_private_key_encrypted.encode(),
            password=None
        )

        valid_bids = []
        for bid in product.bids:
            # Desencriptar valor
            try:
                encrypted_bytes = base64.b64decode(bid.encrypted_value)
                decrypted = private_key.decrypt(
                    encrypted_bytes,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                bid_value = int(decrypted.decode())

                # Validar commitment
                hash_input = f"{bid_value}{bid.salt}".encode()
                expected_commitment = hashlib.sha256(hash_input).hexdigest()

                if expected_commitment == bid.commitment_hash:
                    valid_bids.append((bid_value, bid.user_id))
            except Exception as e:
                continue  # ignorar bid inválida
        if valid_bids:
            winner_bid = max(valid_bids, key=lambda x: x[0])
            product.winner_id = winner_bid[1]

    db.commit()