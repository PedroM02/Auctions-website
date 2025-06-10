# app/crud/product.py

import base64
import hashlib
import os
import shutil
import logging

from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import List
from datetime import datetime
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from ..utils.vdf import *
from ..utils.crypto import *
from ..models.models import Product
from .user import get_user_by_id


lisbon_tz = ZoneInfo("Europe/Lisbon")
utc_tz = ZoneInfo("UTC")
logger = logging.getLogger("LS")

def get_valid_bids_for_product(db: Session, product: Product):
    if not product.rsa_private_key_encrypted:
        return []

    try:
        # execute the vdf
        secret = base64.b64decode(product.vdf_secret)
        modulus = int(product.vdf_modulus)
        difficulty = product.vdf_difficulty
        vdf_params = {
            "modulus": modulus,
            "generator": 5,
            "delay": difficulty
        }

        output, _ = eval_vdf(vdf_params, secret)
        vdf_key = hashlib.sha256(str(output).encode()).digest()

        # decrypt private_key
        decrypted_pem = decrypt_with_vdf_key(vdf_key, product.rsa_private_key_encrypted)
        if not decrypted_pem.startswith("-----BEGIN"):
            raise ValueError(f"Malformed PEM key for product with id {product.id}")

        private_key = load_pem_private_key(decrypted_pem.encode("utf-8"), password=None)

    except Exception as e:
        logger.warning(f"Error creating product(id:{product.id})'s key ", exc_info=True)
        return []

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
        except Exception as e:
            logger.warning(f"Error validating user(id: {bid.user_id})'s bid", exc_info=True)
            continue
    # sort the bids first by value in descending order, then by time_stamp in ascending order
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

    valid_bids = []
    if product.end_date <= datetime.now(tz=utc_tz):
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

def create_new_product(user_id: any,
                       name: str,
                       description: str,
                       base_value: int, 
                       end_dt: datetime, 
                       photos: List[UploadFile], 
                       db: Session, 
                       start_dt: datetime):

    # create VDF params
    difficulty = 50_000
    vdf_params = setup(delay=difficulty)
    modulus = vdf_params["modulus"]

    private_key, private_pem, public_pem = generate_rsa_keys()

    secret = os.urandom(32)  # VDF secret
    output, proof = eval_vdf(vdf_params, secret)

    vdf_key = hashlib.sha256(str(output).encode()).digest()
    encrypted_private_key = encrypt_with_vdf_key(vdf_key, private_pem.encode("utf-8"))

    photo_paths = []
    os.makedirs("static/product_photos", exist_ok=True)
    for photo in photos:
        if photo.filename:
            filename = f"{datetime.now(utc_tz).timestamp()}_{photo.filename}"
            path = os.path.join("static/product_photos", filename)
            with open(path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            photo_paths.append(f"/static/product_photos/{filename}")

    new_product = Product(
        name=name,
        description=description,
        base_value=base_value,
        start_date=start_dt,
        end_date=end_dt,
        photos=";".join(photo_paths),
        seller_id=user_id,
        winner_id=None,
        product_type_id=None,
        rsa_public_key=public_pem,
        rsa_private_key_encrypted=encrypted_private_key,
        vdf_secret=base64.b64encode(secret).decode(),
        vdf_modulus=str(modulus),
        vdf_difficulty=difficulty,
        vdf_start_time=None,
        vdf_output=output,
        vdf_proof=proof
    )

    db.add(new_product)
    db.commit()


    
def finalize_expired_auctions(db: Session):
    now = datetime.now(tz=utc_tz)
    products = db.query(Product).filter(
        Product.end_date <= now,
        Product.winner_id == None
    ).all()

    for product in products:
        try:
            product.vdf_start_time = now

            secret = base64.b64decode(product.vdf_secret)
            modulus = int(product.vdf_modulus)
            difficulty = product.vdf_difficulty
            vdf_params = {
                "modulus": modulus,
                "generator": 5,
                "delay": difficulty
            }

            # evaluate VDF
            output, proof = eval_vdf(vdf_params, secret)
            product.vdf_proof = proof
            product.vdf_output = str(output)

            # decrypt private_key
            logger.info(f"Decrypting private_key from product with id {product.id}")
            vdf_key = hashlib.sha256(str(output).encode()).digest()
            decrypted_pem = decrypt_with_vdf_key(vdf_key, product.rsa_private_key_encrypted)
            logger.debug(f"🔍 PEM decrypted for product with id {product.id}:\n{decrypted_pem}")
            if not decrypted_pem.startswith("-----BEGIN"):
                raise ValueError(f"Malformed PEM key for product with id {product.id}")
            private_key = load_pem_private_key(decrypted_pem.encode("utf-8"), password=None)

            valid_bids = []
            logger.info(f"Evaluating {len(product.bids)} bids for product with id {product.id}")
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
                        valid_bids.append((bid_value, bid.user_id))
                except Exception as e:
                    logger.warning(f"Error processing bid with id {bid.id} for product with id {product.id}", exc_info=True)
                    continue

            if valid_bids:
                winner_bid = max(valid_bids, key=lambda x: x[0])
                product.winner_id = winner_bid[1]
                logger.info(f"Product with id {product.id} assigned to the user with id {winner_bid[1]} with value {winner_bid[0]}")

        except Exception as e:
            logger.error(f"Error finishing the auction of the product with id {product.id}", exc_info=True)
            continue

    db.commit()