from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependecies import pegar_sessao
from schemas import PedidoSchema
from models import Pedidos


order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get("/")
async def orders():
    """Essa é a rota padrão de pedidos, onde você pode acessar as informações dos pedidos.
        Todas as rotas de pedidos devem passar por essa verificação."""
    return {"message": "Você acessou a rota de pedidos"}

@order_router.post("/pedidos")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    novo_pedido = Pedidos(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {"message": f"Pedido criado com sucesso para o usuário {novo_pedido.usuario}"}
    