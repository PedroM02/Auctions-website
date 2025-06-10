# main.py
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from .private import section_key
from .api import bid, product, home, auth, user
from .db.connection import Base, engine

# Configuração global de logging
logging.basicConfig(
    level=logging.INFO,  # Podes mudar para DEBUG, WARNING, etc.
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("LS")
logger.info("Iniciando aplicação FastAPI")

# Inicializar base de dados
Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI()

# Montar recursos estáticos e rotas
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(bid.router)
app.include_router(product.router)
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(user.router)

# Middleware de sessão
app.add_middleware(SessionMiddleware, secret_key=section_key)
