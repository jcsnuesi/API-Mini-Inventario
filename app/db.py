
import motor.motor_asyncio
from pymongo import ASCENDING
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


MONGO_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "inventory_db")

# Variables globales
client = None
db = None

async def init_db():
    """Inicializar conexión a la base de datos"""
    global client, db
    
    try:
        print(f"🔗 Conectando a MongoDB Atlas...")
        
        # Ocultar credenciales en el log
        safe_url = MONGO_URL
        if '@' in MONGO_URL:
            safe_url = MONGO_URL.split('@')[0] + '@[oculto]'
        print(f"   URL: {safe_url}")
        
        # Crear cliente
        client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGO_URL, 
            serverSelectionTimeoutMS=10000
        )
        
        # Probar conexión
        await client.admin.command('ping')
        
        # Asignar base de datos
        db = client[DATABASE_NAME]
        
        print(f" Conectado exitosamente a: {DATABASE_NAME}")
        
        # Intentar crear índices (manejar error si no hay permisos)
        try:
            await db.products.create_index([("sku", ASCENDING)], unique=True)
            print(" Índice único creado para 'sku'")
        except Exception as e:
            print(f"  No se pudo crear índice 'sku': {e}")
            
        try:
            await db.movements.create_index([("product_id", ASCENDING), ("ts", ASCENDING)])
            print(" Índice compuesto creado para 'movements'")
        except Exception as e:
            print(f"  No se pudo crear índice 'movements': {e}")
        
        return True
        
    except Exception as e:
        print(f" Error conectando a MongoDB: {type(e).__name__}")
        print(f"   Detalle: {str(e)[:200]}")
        
        # Aún así crear un cliente y db aunque falle la conexión
       
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
            db = client[DATABASE_NAME]
            print("⚠️  Usando conexión 'dummy' - operaciones fallarán")
        except:
            pass
            
        return False

def get_db():
    """Obtener instancia de la base de datos"""
    global db
    if db is None:
        print("  ADVERTENCIA: Base de datos no inicializada")
        print(" Asegúrate de llamar a init_db() en startup")
    
    return db