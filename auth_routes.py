"""Rotas de autenticação e gerenciamento de usuários.

Este módulo contém todas as endpoints relacionadas a autenticação,
criação de conta, login e refresh de tokens JWT.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from sqlalchemy.orm import Session
from dependencies import get_session, verify_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UserSchema, LoginSchema
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

# Router para rotas de autenticação
auth_router = APIRouter(prefix="/auth", tags=["auth"])


def create_token(user_id: int, duration: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    """Cria um token JWT para um usuário.
    
    Args:
        user_id: ID do usuário
        duration: Duração de validade do token (padrão: ACCESS_TOKEN_EXPIRE_MINUTES)
        
    Returns:
        str: Token JWT codificado
    """
    expire_date = datetime.now(timezone.utc) + duration
    info_dict = {"sub": str(user_id), "exp": expire_date}
    encoded_jwt = jwt.encode(info_dict, SECRET_KEY, algorithm=ALGORITHM)    
    return encoded_jwt

def auth_user(email: str, senha: str, session: Session) -> User | bool:
    """Autentica um usuário verificando email e senha.
    
    Args:
        email: Email do usuário
        senha: Senha fornecida pelo usuário
        session: Sessão do banco de dados
        
    Returns:
        User: Objeto do usuário se autenticação for bem-sucedida
        bool: False se autenticação falhar
    """
    user = session.query(User).filter(User.email==email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(senha, user.password):
        return False
    return user

@auth_router.get("/login")
async def auth() -> dict:
    """Retorna mensagem de boas-vindas na rota padrão de autenticação.
    
    Returns:
        dict: Mensagem de informação sobre autenticação
    """
    return {"message": "Você está na rota padrão de autenticação!", "autenticado": False}

@auth_router.post("/create-account")
async def create_account(user_schema: UserSchema, session: Session = Depends(get_session)) -> dict:
    """Cria uma nova conta de usuário no sistema.
    
    Args:
        user_schema: Dados do novo usuário
        session: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de sucesso com email do usuário criado
        
    Raises:
        HTTPException: Se o email já estiver cadastrado
    """
    usuario = session.query(User).filter(User.email==user_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="O email do usuário já está cadastrado no sistema!")
    else:
        criptografied_password = bcrypt_context.hash(user_schema.password[:72]) # Criptografa a senha usando o bcrypt
        novo_usuario = User(name=user_schema.name, email=user_schema.email, password=criptografied_password, active=user_schema.active, admin=user_schema.admin) # Cria um novo usuário com os dados fornecidos
        session.add(novo_usuario)
        session.commit()
        return {"message": f"Usuário criado com sucesso! {user_schema.email}"}
    
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(get_session)) -> dict:
    """Autentica um usuário e retorna tokens de acesso.
    
    Args:
        login_schema: Email e senha do usuário
        session: Sessão do banco de dados
        
    Returns:
        dict: Access token, refresh token e tipo de token (bearer)
        
    Raises:
        HTTPException: Se as credenciais forem inválidas
    """
    user = auth_user(login_schema.email, login_schema.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas!")
    else:
        access_token = create_token(user.id)
        refresh_token = create_token(user.id, duration=timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token, 
            "token_type": "bearer"
            }
    
@auth_router.post("/login-form")
async def login_form(data_form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)) -> dict:
    """Autentica um usuário via formulário padrão OAuth2.
    
    Args:
        data_form: Formulário com username (email) e password
        session: Sessão do banco de dados
        
    Returns:
        dict: Access token e tipo de token (bearer)
        
    Raises:
        HTTPException: Se as credenciais forem inválidas
    """
    user = auth_user(data_form.username, data_form.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas!")
    else:
        access_token = create_token(user.id)
        return {
            "access_token": access_token,
            "token_type": "bearer"
            }
        
@auth_router.get("/refresh")
async def use_refresh_token(user: User = Depends(verify_token)) -> dict:
    """Renova o token de acesso usando um token válido.
    
    Args:
        user: Usuário autenticado
        
    Returns:
        dict: Novo access token e tipo de token (bearer)
    """
    access_token = create_token(user.id)
    return {
            "access_token": access_token,
            "token_type": "bearer"
            }
        
