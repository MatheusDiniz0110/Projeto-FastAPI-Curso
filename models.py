"""Modelos do banco de dados SQLAlchemy.

Este módulo define as estruturas de dados para usuários, pedidos e itens de pedidos
usando SQLAlchemy ORM com banco de dados SQLite.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils.types import ChoiceType

# Cria a conexão com o banco de dados SQLite
db = create_engine('sqlite:///banco.db')

# Cria a classe base para os modelos do SQLAlchemy
Base = declarative_base()


class User(Base):
    """Modelo de usuário do sistema.
    
    Atributos:
        id (int): Identificador único do usuário (chave primária)
        name (str): Nome do usuário
        email (str): Email único do usuário
        password (str): Senha criptografada do usuário
        active (bool): Indica se o usuário está ativo (padrão: True)
        admin (bool): Indica se o usuário é administrador (padrão: False)
    """
    __tablename__ = 'Users'

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    email = Column("email", String, nullable=False, unique=True)
    password = Column("password", String)
    active = Column("active", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, name: str, email: str, password: str, active: bool = True, admin: bool = False) -> None:
        """Inicializa um novo usuário.
        
        Args:
            name: Nome do usuário
            email: Email único do usuário
            password: Senha criptografada do usuário
            active: Se o usuário está ativo (padrão: True)
            admin: Se o usuário é administrador (padrão: False)
        """
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin


class Order(Base):
    """Modelo de pedido do sistema.
    
    Atributos:
        id (int): Identificador único do pedido (chave primária)
        status (str): Status do pedido (PENDENTE, FINALIZADO, CANCELADO) - padrão: PENDENTE
        user_id (int): ID do usuário que fez o pedido (chave estrangeira)
        price (float): Preço total do pedido (padrão: 0.0)
        items (list): Lista de itens no pedido com cascata de deleção
    """
    __tablename__ = 'Orders'

    # STATUS_ORDERS = (
    #     ("PENDENTE", "PENDENTE"),
    #     ("FINALIZADO", "FINALIZADO"),
    #     ("CANCELADO", "CANCELADO")
    # )

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    user_id = Column("user_id", ForeignKey('Users.id'))
    price = Column("price", Float)
    items = relationship("Item", cascade="all, delete")

    def __init__(self, user_id: int, status: str = "PENDENTE",  price: float = 0.0) -> None:
        """Inicializa um novo pedido.
        
        Args:
            user_id: ID do usuário que faz o pedido
            status: Status inicial do pedido (padrão: PENDENTE)
            price: Preço inicial do pedido (padrão: 0.0)
        """
        self.status = status
        self.user_id = user_id
        self.price = price

    def calculate_price(self) -> None:
        """Calcula o preço total do pedido baseado na soma dos itens.
        
        O preço é calculado como: sum(item.unit_price * item.quantity para cada item)
        """
        self.price = sum(item.unit_price * item.quantity for item in self.items)


class Item(Base):
    """Modelo de item do pedido.
    
    Atributos:
        id (int): Identificador único do item (chave primária)
        quantity (int): Quantidade do item no pedido
        flavor (str): Sabor ou descrição do item
        size (str): Tamanho do item
        unit_price (float): Preço unitário do item
        order_id (int): ID do pedido ao qual o item pertence (chave estrangeira)
    """
    __tablename__ = 'Items'

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantity = Column("quantity", Integer)
    flavor = Column("flavor", String)
    size = Column("size", String)
    unit_price = Column("unit_price", Float)
    order_id = Column("order_id", ForeignKey('Orders.id'))

    def __init__(self, quantity: int, flavor: str, size: str, unit_price: float, order_id: int) -> None:
        """Inicializa um novo item de pedido.
        
        Args:
            quantity: Quantidade do item
            flavor: Sabor ou descrição do item
            size: Tamanho do item
            unit_price: Preço unitário do item
            order_id: ID do pedido ao qual o item pertence
        """
        self.quantity = quantity
        self.flavor = flavor
        self.size = size
        self.unit_price = unit_price
