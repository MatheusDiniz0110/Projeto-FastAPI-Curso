from fastapi import APIRouter, HTTPException, Depends
from models import User
from sqlalchemy.orm import Session
from dependencies import get_session
from main import bcrypt_context
from schemas import UserSchema, LoginSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(user_id):
    token = f"aimeucuzinho{user_id}1234567890"
    return token

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
    '''
    Essa é a rota de login do nosso sistema. Ela deve receber o email e a senha do usuário, verificar se o email existe no banco de dados e se a senha está correta.
    '''
    user = session.query(User).filter(User.email==login_schema.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado!")
    else:
        access_token = criar_token(user.id)
        return {
            "access_token": access_token, 
            "token_type": "bearer"
            }
        
        # JWT Bearer
        # header = {"Authorization": f"Bearer {access_token}"}

