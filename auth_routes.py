from fastapi import APIRouter, HTTPException, Depends
from models import User, db
from sqlalchemy.orm import sessionmaker
from dependencies import get_session
from main import bcrypt_context

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/login")
async def auth():
    '''
    Essa é a rota padrão de autenticação do nosso sistema.
    '''
    return {"message": "Você está na rota padrão de autenticação!", "autenticado": False}

@auth_router.post("/create-account")
async def create_account(name: str, email: str, password: str, session=Depends(get_session)):
    usuario = session.query(User).filter_by(email=email).first() # Faz a busca de um possível usuário ja existente com o mesmo email
    if usuario: # Verifica se o usuário já existe
        raise HTTPException(status_code=400, detail="O email do usuário já está cadastrado no sistema!")
        # return {"message": "Usuário já existe!"}
    else:
        criptografied_password = bcrypt_context.hash(password[:72]) # Criptografa a senha usando o bcrypt
        novo_usuario = User(name=name, email=email, password=criptografied_password) # Cria um novo usuário com os dados fornecidos
        session.add(novo_usuario)
        session.commit()
        return {"message": f"Usuário criado com sucesso! {email}"}

