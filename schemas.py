"""Esquemas Pydantic para validação de dados da API.

Este módulo define os modelos de validação para requisições e respostas da API.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserSchema(BaseModel):
    """Esquema de validação para criação de usuário.
    
    Atributos:
        name: Nome do usuário
        email: Email do usuário
        password: Senha do usuário
        active: Se o usuário está ativo (opcional, padrão: True)
        admin: Se o usuário é administrador (opcional, padrão: False)
    """
    name: str
    email: str
    password: str
    active: Optional[bool] = True
    admin: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

class OrderSchema(BaseModel):
    """Esquema de validação para criação de pedido.
    
    Atributos:
        user_id: ID do usuário que faz o pedido
    """
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class LoginSchema(BaseModel):
    """Esquema de validação para login.
    
    Atributos:
        email: Email do usuário
        password: Senha do usuário
    """
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class ItemSchema(BaseModel):
    """Esquema de validação para item de pedido.
    
    Atributos:
        quantity: Quantidade do item
        flavor: Sabor do item
        size: Tamanho do item
        unit_price: Preço unitário do item
    """
    quantity: int
    flavor: str
    size: str
    unit_price: float

    model_config = ConfigDict(from_attributes=True)