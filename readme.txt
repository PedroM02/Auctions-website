# Sealed-Bid Auction Website

A sealed-bid auction is a type of auction in which, while it is ongoing, nobody can see the bids
already made by potential buyers. The focus here is : nobody can see the bids already made.
This is where cryptographic tools like RSA and Verifiable Delay Functions (VDFs) come into
play.
In this project I developed a sealed-bid web application using modern tools and crypto-
graphic primitives. The backend was built with Python, using the FastAPI framework and
SQLAlchemy for API management and database interaction. DBeaver was used for visualizing
and managing the database. For cryptographic security, RSA encryption and a custom imple-
mentation of a Verifiable Delay Function, inspired by the work of Boneh et al. [1]. Celery was
employed to execute parallel tasks independently of the API, and Docker was used to orchestrate
the initialization and deployment of all components.
The main goal of this project was to explore the use of VDFs in a practical setting, demon-
strating how they can be applied to delay decryption in time-sensitive applications such as
auctions.

---

## Getting Started with Docker

### 1. Clone the repository

<pre>```bash git clone https://github.com/PedroM02/Auctions-website.git cd sealed-bid-auction```</pre>

### 2. Build and run all services

<pre>```bash
docker-compose up --build```
</pre>

### 3. To stop the services

<pre>```bash
docker-compose down```
</pre>

### 4. to remove volumes and containers

<pre>```bash
docker-compose down -v --remove-orphans```
</pre>
