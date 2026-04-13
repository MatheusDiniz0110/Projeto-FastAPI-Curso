from fastapi import APIRouter, Depends
from dependencies import get_session
from sqlalchemy.orm import Session
from schemas import OrderSchema
from models import Order

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get("/")
async def orders():
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas de pedidos precisam de autenticação.
    """
    return {"message": "Você está na rota de pedidos!"}

@order_router.post('/create_order')
async def create_order(order_schema: OrderSchema, session: Session = Depends(get_session)):
    """
    Essa é a rota de criação de pedidos do nosso sistema. Ela deve receber os dados do pedido, como os itens, o preço total e o ID do usuário que fez o pedido.
    """
    new_order = Order(user_id=order_schema.user_id) # Create a new order with the provided user_id and a default price of 0.0
    session.add(new_order) # Add the new order to the session
    session.commit() # Commit the session to save the new order in the database
    return {"message": f"Pedido criado com sucesso! ID do pedido: {new_order.id}"}