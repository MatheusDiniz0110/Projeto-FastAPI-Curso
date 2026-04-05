from fastapi import APIRouter

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get("/")
async def orders():
    """Essa é a rota padrão de pedidos, onde você pode acessar as informações dos pedidos.
        Todas as rotas de pedidos devem passar por essa verificação."""
    return {"message": "Você acessou a rota de pedidos"}