"""Testes automatizados da aplicação FastAPI.

Este módulo contém testes abrangentes para todas as rotas e funcionalidades
do sistema de gerenciamento de pedidos, incluindo autenticação, criação de
pedidos e gerenciamento de itens.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User, Order, Item
from main import app
from dependencies import get_session
from datetime import datetime, timedelta, timezone
from main import bcrypt_context, SECRET_KEY, ALGORITHM
from jose import jwt

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria as tabelas de teste
Base.metadata.create_all(bind=engine)


def override_get_session():
    """Override da dependência get_session para usar banco de dados de teste."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Configura e limpa o banco de dados antes e depois de cada teste."""
    # Setup: Cria todas as tabelas
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: Remove todas as tabelas
    Base.metadata.drop_all(bind=engine)


def create_test_user(email: str = "test@test.com", password: str = "test123", admin: bool = False) -> User:
    """Cria um usuário de teste no banco de dados.
    
    Args:
        email: Email do usuário
        password: Senha do usuário (será criptografada)
        admin: Se o usuário é administrador
        
    Returns:
        User: Objeto do usuário criado
    """
    db = TestingSessionLocal()
    hashed_password = bcrypt_context.hash(password)
    user = User(name="Test User", email=email, password=hashed_password, admin=admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def create_token(user_id: int) -> str:
    """Cria um token JWT para testes.
    
    Args:
        user_id: ID do usuário
        
    Returns:
        str: Token JWT válido
    """
    expire_date = datetime.now(timezone.utc) + timedelta(minutes=30)
    info_dict = {"sub": str(user_id), "exp": expire_date}
    encoded_jwt = jwt.encode(info_dict, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ========== TESTES DE AUTENTICAÇÃO ==========

def test_auth_get_login_default():
    """Testa a rota GET /auth/login (rota padrão)."""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert "Você está na rota padrão de autenticação!" in response.json()["message"]


def test_create_account_success():
    """Testa criação bem-sucedida de uma nova conta."""
    response = client.post(
        "/auth/create-account",
        json={
            "name": "New User",
            "email": "newuser@test.com",
            "password": "securepass123"
        }
    )
    assert response.status_code == 200
    assert "Usuário criado com sucesso" in response.json()["message"]


def test_create_account_duplicate_email():
    """Testa que não é possível criar duas contas com o mesmo email."""
    create_test_user(email="duplicate@test.com")
    
    response = client.post(
        "/auth/create-account",
        json={
            "name": "Another User",
            "email": "duplicate@test.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "email do usuário já está cadastrado" in response.json()["detail"]


def test_login_success():
    """Testa login bem-sucedido."""
    create_test_user(email="login@test.com", password="password123")
    
    response = client.post(
        "/auth/login",
        json={
            "email": "login@test.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_email():
    """Testa login com email inexistente."""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@test.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "não encontrado ou credenciais inválidas" in response.json()["detail"]


def test_login_invalid_password():
    """Testa login com senha incorreta."""
    create_test_user(email="user@test.com", password="correctpassword")
    
    response = client.post(
        "/auth/login",
        json={
            "email": "user@test.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 400
    assert "não encontrado ou credenciais inválidas" in response.json()["detail"]


def test_refresh_token_success():
    """Testa renovação bem-sucedida de token."""
    user = create_test_user(email="refresh@test.com")
    token = create_token(user.id)
    
    response = client.get(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_refresh_token_invalid():
    """Testa renovação com token inválido."""
    response = client.get(
        "/auth/refresh",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


# ========== TESTES DE ROTAS DE PEDIDOS ==========

def test_get_orders_default():
    """Testa a rota GET /orders/ (rota padrão de pedidos)."""
    user = create_test_user()
    token = create_token(user.id)
    
    response = client.get(
        "/orders/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_orders_without_token():
    """Testa que a rota de pedidos requer autenticação."""
    response = client.get("/orders/")
    assert response.status_code in [401, 403]


def test_create_order_success():
    """Testa criação bem-sucedida de pedido."""
    user = create_test_user()
    token = create_token(user.id)
    
    response = client.post(
        "/orders/create_order",
        json={"user_id": user.id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "ID do pedido:" in response.json()["message"]
    assert response.json()["message"] != ""


def test_cancel_order_success():
    """Testa cancelamento bem-sucedido de pedido."""
    user = create_test_user()
    token = create_token(user.id)
    
    # Cria um pedido
    db = TestingSessionLocal()
    order = Order(user_id=user.id)
    db.add(order)
    db.commit()
    db.refresh(order)
    order_id = order.id
    db.close()
    
    # Cancela o pedido
    response = client.post(
        f"/orders/order/cancel/{order_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "cancelado com sucesso" in response.json()["message"]


def test_cancel_order_not_found():
    """Testa cancelamento de pedido inexistente."""
    user = create_test_user()
    token = create_token(user.id)
    
    response = client.post(
        "/orders/order/cancel/999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "Pedido não encontrado" in response.json()["detail"]


def test_cancel_order_unauthorized():
    """Testa que usuário não pode cancelar pedido de outro usuário."""
    user1 = create_test_user(email="user1@test.com")
    user2 = create_test_user(email="user2@test.com")
    token = create_token(user2.id)
    
    # Cria um pedido para user1
    db = TestingSessionLocal()
    order = Order(user_id=user1.id)
    db.add(order)
    db.commit()
    db.refresh(order)
    order_id = order.id
    db.close()
    
    # user2 tenta cancelar
    response = client.post(
        f"/orders/order/cancel/{order_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert "autorização" in response.json()["detail"].lower()


def test_list_orders_admin_only():
    """Testa que apenas administradores podem listar pedidos."""
    regular_user = create_test_user(email="user@test.com", admin=False)
    admin_user = create_test_user(email="admin@test.com", admin=True)
    
    # Tenta listrar como usuário regular
    regular_token = create_token(regular_user.id)
    response = client.get(
        "/orders/list",
        headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 401
    
    # Lista como administrador
    admin_token = create_token(admin_user.id)
    response = client.get(
        "/orders/list",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "orders" in response.json()


def test_add_item_to_order_success():
    """Testa adição bem-sucedida de item a pedido."""
    user = create_test_user()
    token = create_token(user.id)
    
    # Cria um pedido
    db = TestingSessionLocal()
    order = Order(user_id=user.id)
    db.add(order)
    db.commit()
    db.refresh(order)
    order_id = order.id
    db.close()
    
    # Adiciona item
    response = client.post(
        f"/orders/order/add_item/{order_id}",
        json={
            "quantity": 2,
            "flavor": "chocolate",
            "size": "large",
            "unit_price": 10.50
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Item criado com sucesso" in response.json()["message"]
    assert response.json()["price_order"] == 21.0  # 2 * 10.50


def test_add_item_to_nonexistent_order():
    """Testa adição de item a pedido inexistente."""
    user = create_test_user()
    token = create_token(user.id)
    
    response = client.post(
        "/orders/order/add_item/999",
        json={
            "quantity": 1,
            "flavor": "vanilla",
            "size": "medium",
            "unit_price": 5.00
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "Pedido não encontrado" in response.json()["detail"]


def test_remove_item_from_order_success():
    """Testa remoção bem-sucedida de item de pedido."""
    user = create_test_user()
    token = create_token(user.id)
    
    # Cria pedido via API
    order_response = client.post(
        "/orders/create_order",
        json={"user_id": user.id},
        headers={"Authorization": f"Bearer {token}"}
    )
    order_msg = order_response.json()["message"]
    order_id = int(order_msg.split()[-1])
    
    # Adiciona item via API
    item_response = client.post(
        f"/orders/order/add_item/{order_id}",
        json={
            "quantity": 2,
            "flavor": "chocolate",
            "size": "large",
            "unit_price": 10.0
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    item_id = item_response.json()["item_id"]
    
    # Remove o item
    response = client.post(
        f"/orders/order/remove_item/{item_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Item removido com sucesso" in response.json()["message"]
    assert response.json()["price_order"] == 0.0


def test_remove_item_not_found():
    """Testa remoção de item inexistente."""
    user = create_test_user()
    token = create_token(user.id)
    
    response = client.post(
        "/orders/order/remove_item/999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "Item do pedido não encontrado" in response.json()["detail"]


def test_remove_item_unauthorized():
    """Testa que usuário não pode remover item de pedido de outro usuário."""
    user1 = create_test_user(email="user1@test.com")
    user2 = create_test_user(email="user2@test.com")
    
    # Cria pedido e item para user1
    db = TestingSessionLocal()
    order = Order(user_id=user1.id)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    item = Item(quantity=1, flavor="vanilla", size="small", unit_price=5.0, order_id=order.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    item_id = item.id
    db.close()
    
    # user2 tenta remover
    token = create_token(user2.id)
    response = client.post(
        f"/orders/order/remove_item/{item_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [400, 401] # Pode retornar 400 se não conseguir achar o relacionamento


# ========== TESTES DE LÓGICA DE NEGÓCIO ==========

def test_order_calculate_price():
    """Testa cálculo correto do preço total do pedido."""
    from sqlalchemy import inspect
    db = TestingSessionLocal()
    
    # Cria usuário
    user = User(name="Test", email="calcprice@test.com", password="pass")
    db.add(user)
    db.flush()
    
    order = Order(user_id=user.id)
    db.add(order)
    db.flush()
    order_id = order.id
    
    item1 = Item(quantity=2, flavor="chocolate", size="large", unit_price=10.0, order_id=order_id)
    item2 = Item(quantity=3, flavor="vanilla", size="small", unit_price=5.0, order_id=order_id)
    
    db.add(item1)
    db.add(item2)
    db.commit()
    
    # Mantém a sessão para acessar os relacionamentos
    order = db.query(Order).filter(Order.id == order_id).first()
    order.calculate_price()
    
    # 2*10 + 3*5 = 20 + 15 = 35
    assert order.price == 35.0
    db.close()


def test_admin_can_modify_other_users_orders():
    """Testa que administrador pode modificar pedidos de outros usuários."""
    user = create_test_user(email="user@test.com", admin=False)
    admin = create_test_user(email="admin@test.com", admin=True)
    admin_token = create_token(admin.id)
    
    # Cria um pedido para usuário regular
    db = TestingSessionLocal()
    order = Order(user_id=user.id)
    db.add(order)
    db.commit()
    db.refresh(order)
    order_id = order.id
    db.close()
    
    # Admin cancela o pedido
    response = client.post(
        f"/orders/order/cancel/{order_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "cancelado com sucesso" in response.json()["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
