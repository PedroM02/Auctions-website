# Sealed-Bid Auction Website

A sealed-bid auction is a type of auction in which, while it is ongoing, nobody can see the bids
that have already been submitted by potential buyers. The key principle is that **no one can see the current bids**.

To enforce this confidentiality, cryptographic tools like RSA and Verifiable Delay Functions (VDFs) are used.

In this project, I developed a sealed-bid web application using modern tools and cryptographic primitives.  
The backend is built with **Python** using the **FastAPI** framework and **SQLAlchemy** for database interactions.  
**DBeaver** was used for visualizing and managing the database. For cryptographic security, I implemented **RSA encryption** and a custom **Verifiable Delay Function (VDF)**, inspired by the work of Boneh et al.  
**Celery** is used to execute background tasks independently of the API, and **Docker** is used to orchestrate and deploy all components.

The main goal of this project is to explore the use of VDFs in a practical setting, demonstrating how they can delay decryption in time-sensitive applications such as auctions.

---

## Downloads

### Git
To clone the project you will need to have git installed, in case you don't have it you can download it here https://github.com/git-guides/install-git

### Docker Desktop
In case you don't have Docker you can download it here https://www.docker.com/products/docker-desktop/


---


## Getting Started with Docker

### 1. Clone the repository or download the .zip

```bash
git clone https://github.com/PedroM02/Auctions-website.git
```
```bash
cd Auctions-website
```

### 2. Create private.py and Docker download

To run the project you need to create the file .app/private.py with the following code:

```python
db_pass = "your_db_pass"  # default password = 1234
section_key = "your_random_section_key"
```

Run the docker desktop.

### 3. Build and run all services

```bash
docker-compose up --build
```

To see the website open the locahost:8000 link on the browser.

### 4. To stop the services

```bash
docker-compose down
```

Or simply do (ctrl c) on terminal.

### 5. To remove volumes and containers

```bash
docker-compose down -v --remove-orphans
```
