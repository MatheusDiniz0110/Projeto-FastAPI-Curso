"""Rotas de gerenciamento de pedidos.

Este módulo contém todas as endpoints relacionadas ao gerenciamento de pedidos,
incluindo criação, listagem, cancelamento e gerenciamento de itens.
"""
from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session, verify_token
from sqlalchemy.orm import Session
from schemas import OrderSchema, ItemSchema
from models import Order, User, Item

# Router com prefixo /orders, requer autenticação para todas as rotas
order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verify_token)])


@order_router.get("/")
async def orders() -> dict:
    """Retorna mensagem de boas-vindas na rota padrão de pedidos.
    
    Returns:
        dict: Mensagem de confirmação de acesso
    """
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas de pedidos precisam de autenticação.
    """
    return {"message": "Você está na rota de pedidos!"}

@order_router.post('/create_order')
async def create_order(order_schema: OrderSchema, session: Session = Depends(get_session)) -> dict:
    """Cria um novo pedido no sistema.
    
    Args:
        order_schema: Dados do pedido contendo user_id
        session: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de sucesso com o ID do pedido criado
        
    Raises:
        HTTPException: Se houver erro ao criar o pedido
    """
    new_order = Order(user_id=order_schema.user_id) # Create a new order with the provided user_id and a default price of 0.0
    session.add(new_order) # Add the new order to the session
    session.commit() # Commit the session to save the new order in the database
    return {"message": f"Pedido criado com sucesso! ID do pedido: {new_order.id}"}

@order_router.post('/order/cancel/{order_id}')
async def cancel_order(order_id: int, session: Session = Depends(get_session), user: User = Depends(verify_token)) -> dict:
    """Cancela um pedido existente.
    
    Args:
        order_id: ID do pedido a ser cancelado
        session: Sessão do banco de dados
        user: Usuário autenticado
        
    Returns:
        dict: Mensagem de sucesso e ID do pedido cancelado
        
    Raises:
        HTTPException: Se o pedido não existir ou o usuário não tiver autorização
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not user.admin and order.user_id != user.id:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")

    order.status = "CANCELADO"
    session.commit()
    return {
        "message": f"Pedido com ID {order.id} cancelado com sucesso!",
        "order_id": order.id,
        "status": order.status
    }

@order_router.get('/list')
async def list_orders(session: Session = Depends(get_session), user: User = Depends(verify_token)) -> dict:
    """Lista todos os pedidos (apenas para administradores).
    
    Args:
        session: Sessão do banco de dados
        user: Usuário autenticado
        
    Returns:
        dict: Lista com todos os pedidos do sistema
        
    Raises:
        HTTPException: Se o usuário não for administrador
    """
    if not user.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para acessar essa rota") # If the user is not an admin, raise a 403 error
    else:
        orders = session.query(Order).all() # Query the database for all orders
        return {"orders": orders}
    
@order_router.post("/order/add_item/{order_id}")
async def add_item_to_order(order_id: int, item_schema: ItemSchema, session: Session = Depends(get_session), user: User = Depends(verify_token)) -> dict:
    """Adiciona um item a um pedido existente.
    
    Args:
        order_id: ID do pedido
        item_schema: Dados do item a adicionar
        session: Sessão do banco de dados
        user: Usuário autenticado
        
    Returns:
        dict: Dados do item criado e preço atualizado do pedido
        
    Raises:
        HTTPException: Se o pedido não existir ou o usuário não tiver autorização
    """
    order = session.query(Order).filter(Order.id == order_id).first() # Query the database for the order with the specified ID
    if not order:
        raise HTTPException(status_code=400, detail="Pedido não encontrado") # If the order is not found, raise a 400 error
    if user.id != order.user_id and not user.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação") # If the user is not the owner of the order and is not an admin, raise a 403 error
    item_order = Item(item_schema.quantity, item_schema.flavor, item_schema.size, item_schema.unit_price, order_id) # Create a new item with the provided data
    order.items.append(item_order)
    order.calculate_price()
    session.commit()
    return {
        "message": "Item criado com sucesso",
        "item_id": item_order.id,
        "price_order": order.price
    }

@order_router.post("/order/remove_item/{order_item_id}")
async def remove_item_from_order(order_item_id: int, session: Session = Depends(get_session), user: User = Depends(verify_token)) -> dict:
    """Remove um item de um pedido.
    
    Args:
        order_item_id: ID do item a ser removido
        session: Sessão do banco de dados
        user: Usuário autenticado
        
    Returns:
        dict: Mensagem de sucesso, preço atualizado e dados do pedido
        
    Raises:
        HTTPException: Se o item não existir ou o usuário não tiver autorização
    """
    item_order = session.query(Item).filter(Item.id == order_item_id).first()
    if not item_order:
        raise HTTPException(status_code=400, detail="Item do pedido não encontrado")
    
    # Query the associated order
    order = session.query(Order).filter(Order.id == item_order.order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Pedido associado não encontrado")
    
    if user.id != order.user_id and not user.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    session.delete(item_order)
    order.calculate_price()
    session.commit()
    return {
        "message": "Item removido com sucesso",
        "price_order": float(order.price),
        "quantity_items_orders": len(order.items),
        "order_id": order.id
    }