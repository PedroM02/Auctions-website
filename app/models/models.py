# app/models/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text, Table
from sqlalchemy.orm import relationship

from ..db.connection import Base


favourites_table = Table(
    "favourites",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("product.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    birthdate = Column(Date)
    profile_picture = Column(Text)

    bids = relationship("Bid", backref="user")
    favourites = relationship("Product", secondary=favourites_table)


class Product_type(Base):
    __tablename__ = "product_type"


    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    image = Column(Text)

    products = relationship("Product", backref="product_type")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    base_value = Column(Integer)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    vdf_start_time = Column(DateTime)
    vdf_output = Column(Text)
    vdf_secret = Column(String)
    vdf_modulus = Column(String)
    vdf_difficulty = Column(Integer)
    vdf_proof = Column(Text)
    photos = Column(Text)
    seller_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    winner_id = Column(Integer, ForeignKey("user.id"))
    product_type_id = Column(Integer, ForeignKey("product_type.id"))
    rsa_public_key = Column(Text, nullable=True)
    rsa_private_key_encrypted = Column(Text, nullable=True)

    bids = relationship("Bid", backref="product")


class Bid(Base):
    __tablename__ = "bid"

    id = Column(Integer, primary_key=True, index=True)
    time_stamp = Column(DateTime, nullable=False)
    encrypted_value = Column(Text, nullable=False)
    commitment_hash = Column(Text, nullable=False)
    salt = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    product_id = Column(Integer, ForeignKey("product.id"))

