from app.db import get_db

async def get_db_connection():
    """Dependencia para obtener conexión a la base de datos"""
    db = get_db()
    if db is None:
        raise Exception("Database not connected")
    return db