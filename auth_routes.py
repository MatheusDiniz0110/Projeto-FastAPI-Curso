from fastapi import APIRouter, HTTPException, Depends
from models import User 
from sqlalchemy.orm import Session
from dependencies import get_session
from main import bcrypt_context
from schemas import UserSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/login")
async def auth():
    '''
    Essa é a rota padrão de autenticação do nosso sistema.
    '''
    return {"message": "Você está na rota padrão de autenticação!", "autenticado": False}

@auth_router.post("/create-account")
async def create_account(user_schema: UserSchema, session: Session = Depends(get_session)):
    usuario = session.query(User).filter(User.email==user_schema.email).first() # Faz a busca de um possível usuário ja existente com o mesmo email
    if usuario: # Verifica se o usuário já existe
        raise HTTPException(status_code=400, detail="O email do usuário já está cadastrado no sistema!")
    else:
        criptografied_password = bcrypt_context.hash(user_schema.password[:72]) # Criptografa a senha usando o bcrypt
        novo_usuario = User(name=user_schema.name, email=user_schema.email, password=criptografied_password, active=user_schema.active, admin=user_schema.admin) # Cria um novo usuário com os dados fornecidos
        session.add(novo_usuario)
        session.commit()
        return {"message": f"Usuário criado com sucesso! {user_schema.email}"}

