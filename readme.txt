# Sealed-Bid Auction Website

A sealed-bid auction is a type of auction in which, while it is ongoing, nobody can see the bids
that have already been submitted by potential buyers. The key principle is that **no one can see the current bids**.

To enforce this confidentiality, cryptographic tools like RSA and Verifiable Delay Functions (VDFs) are used.

In this project, I developed a sealed-bid web application using modern tools and cryptographic primitives.  
The backend is built with **Python** using the **FastAPI** framework and **SQLAlchemy** for database interactions.  
**DBeaver** was used for visualizing and managing the database. For cryptographic security, I implemented **RSA encryption** and a custom **Verifiable Delay Function (VDF)**, inspired by the work of Boneh et al. [1].  
**Celery** is used to execute background tasks independently of the API, and **Docker** is used to orchestrate and deploy all components.

The main goal of this project is to explore the use of VDFs in a practical setting, demonstrating how they can delay decryption in time-sensitive applications such as auctions.

---

## Getting Started with Docker

### 1. Clone the repository

```bash
git clone https://github.com/PedroM02/Auctions-website.git
cd Auctions-website
```

### 2. Build and run all services

```bash
docker-compose up --build
```

### 3. To stop the services

```bash
docker-compose down
```

### 4. To remove volumes and containers

```bash
docker-compose down -v --remove-orphans
```
