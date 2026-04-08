from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils.types import ChoiceType

# Cria a conexão com o banco de dados SQLite
db = create_engine('sqlite:///banco.db')

# Cria a classe base para os modelos do SQLAlchemy
Base = declarative_base()

# Classes do banco de dados
class User(Base):
    __tablename__ = 'Users'

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    email = Column("email", String, nullable=False, unique=True)
    senha = Column("senha", String)
    ativo = Column("ativo", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, name: str, email: str, senha: str, ativo: bool = True, admin: bool = False):
        self.name = name
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin


class Order(Base):
    __tablename__ = 'Orders'

    STATUS_ORDERS = (
        ("PENDENTE", "PENDENTE"),
        ("FINALIZADO", "FINALIZADO"),
        ("CANCELADO", "CANCELADO")

    )

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", ChoiceType(choices=STATUS_ORDERS), default="PENDENTE")
    user_id = Column("user_id", ForeignKey('Users.id'))
    price = Column("price", Float)
    # items = 

    def __init__(self, user_id: int, price: float, status: str = "PENDENTE"):
        self.status = status
        self.user_id = user_id
        self.price = price


class Item(Base):
    __tablename__ = 'Items'

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantity = Column("quantity", Integer)
    flavor = Column("flavor", String)
    size = Column("size", String)
    unit_price = Column("unit_price", Float)
    order_id = Column("order_id", ForeignKey('Orders.id'))