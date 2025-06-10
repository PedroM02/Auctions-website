# app/crud/bid.py

import hashlib
import os
import base64

from datetime import datetime
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

from ..models.models import Bid, Product


def create_new_bid(db: Session, product: Product, user_id: int, product_id: int, bid_value: int, time_stamp: datetime):

    # random salt
    salt = os.urandom(16).hex()

    # commitment hash = SHA256(valor + salt)
    commitment_input = f"{bid_value}{salt}".encode()
    commitment_hash = hashlib.sha256(commitment_input).hexdigest()


    public_key = serialization.load_pem_public_key(product.rsa_public_key.encode())

    # encrypt the bid with the product's public key
    encrypted_value = public_key.encrypt(
        str(bid_value).encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted_b64 = base64.b64encode(encrypted_value).decode()

    bid = Bid(
        user_id=user_id,
        product_id=product_id,
        encrypted_value=encrypted_b64,
        commitment_hash=commitment_hash,
        salt=salt,
        time_stamp=time_stamp
    )

    db.add(bid)
    db.commit()
    db.refresh(bid)
    return bid
