from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Configurações do JWT
SECRET_KEY = "segredo_super_secreto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Pizzaria API")

# Usuários fictícios
fake_users_db = {
    "cliente1": {
        "username": "cliente1",
        "full_name": "Cliente Um",
        "hashed_password": "senha123",  # Em produção, use hash seguro!
    }
}

# Modelos
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    full_name: str

class Order(BaseModel):
    id: int
    pizza: str
    quantity: int
    customer: str
    created_at: datetime

# Autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or user["hashed_password"] != password:
        return None
    return User(username=user["username"], full_name=user["full_name"])

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        user = fake_users_db.get(username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
        return User(username=user["username"], full_name=user["full_name"])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

# Banco de pedidos fictício
orders_db: List[Order] = []

# Rotas
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/orders", response_model=Order)
async def create_order(order: Order, current_user: User = Depends(get_current_user)):
    order.customer = current_user.username
    order.created_at = datetime.utcnow()
    orders_db.append(order)
    return order

@app.get("/orders", response_model=List[Order])
async def list_orders(current_user: User = Depends(get_current_user)):
    return [order for order in orders_db if order.customer == current_user.username]