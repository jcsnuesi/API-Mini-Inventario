# app/services/stock.py
from app.repositories import products as product_repo

async def check_stock_availability(product_id: str, required_qty: int):
    """Verificar si hay suficiente stock"""
    product = await product_repo.get_product_by_id(product_id)
    if not product:
        return False, "Producto no encontrado"
    
    current_stock = product.get("stock", 0)
    if current_stock >= required_qty:
        return True, "Stock suficiente"
    else:
        return False, f"Stock insuficiente. Disponible: {current_stock}, Requerido: {required_qty}"