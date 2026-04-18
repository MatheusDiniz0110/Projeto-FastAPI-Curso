"""Aplicação principal FastAPI com configuração de autenticação e rotas.

Este módulo inicializa a aplicação FastAPI, configura a autenticação OAuth2,
e incorpora as rotas de autenticação e pedidos.
"""
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

# Variáveis de configuração carregadas do arquivo .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="FastAPI Order System",
    description="Sistema de gerenciamento de pedidos com autenticação JWT",
    version="1.0.0"
)

# Contexto de criptografia bcrypt para senhas
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Esquema OAuth2 para autenticação por token
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)

# Para rodar o aplicativo, use o comando: uvicorn main:app --reload