from fastapi import APIRouter, Depends
from dependencies import get_session
from sqlalchemy.orm import Session
from Schemas import OrderSchema

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
    