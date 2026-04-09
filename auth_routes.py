from fastapi import APIRouter, HTTPException
from models import User, db
from sqlalchemy.orm import sessionmaker

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/login")
async def auth():
    '''
    Essa é a rota padrão de autenticação do nosso sistema.
    '''
    return {"message": "Você está na rota padrão de autenticação!", "autenticado": False}

@auth_router.post("/create-account")
async def create_account(name: str, email: str, password: str):
    Session = sessionmaker(bind=db)
    session = Session()
    usuario = session.query(User).filter_by(email=email).first() # Faz a busca de um possível usuário ja existente com o mesmo email
    if usuario: # Verifica se o usuário já existe
        return {"message": "Usuário já existe!"}
    else:
        novo_usuario = User(name=name, email=email, password=password)
        session.add(novo_usuario)
        session.commit()
        return {"message": "Usuário criado com sucesso!"}

