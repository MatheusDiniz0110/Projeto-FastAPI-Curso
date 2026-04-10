from fastapi import APIRouter, HTTPException, Depends
from models import User
from sqlalchemy.orm import Session
from dependencies import get_session
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UserSchema, LoginSchema
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(user_id):
    expire_date = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    info_dict = {"sub": user_id, "exp": expire_date}
    encoded_jwt = jwt.encode(info_dict, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def auth_user(email, senha, session):
    user = session.query(User).filter(User.email==email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(senha, user.password): # Verifica se a senha fornecida corresponde à senha armazenada no banco de dados
        return False
    return user

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
    
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(get_session)):
    '''Essa é a rota de login do nosso sistema. Ela deve receber o email e a senha do usuário, verificar se o email existe no banco de dados e se a senha está correta.
    '''
    user = auth_user(login_schema.email, login_schema.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas!")
    else:
        access_token = criar_token(user.id)
        return {
            "access_token": access_token, 
            "token_type": "bearer"
            }
        
        # JWT Bearer
        # header = {"Authorization": f"Bearer {access_token}"}

