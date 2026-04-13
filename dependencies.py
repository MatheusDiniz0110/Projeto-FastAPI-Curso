from fastapi import Depends, HTTPException
from sqlalchemy.orm import sessionmaker, Session
from models import db
from models import User
from jose import JWTError, jwt
from main import SECRET_KEY, ALGORITHM, oauth2_schema

def get_session():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def verify_token(token: str = Depends(oauth2_schema), session: Session = Depends(get_session)):
    try:
        dict_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_user = int(dict_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")
    user = session.query(User).filter(User.id==id_user).first()
    if not id_user:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return user

