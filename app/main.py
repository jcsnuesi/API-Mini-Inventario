from fastapi import FastAPI
from datetime import datetime
from app.routers import products, movements
from app.db import init_db

app = FastAPI(
    title="Mini Inventory API",
    description="API REST para gestión de inventario usando FastAPI y MongoDB",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

#  AQUÍ se define el prefix UNA sola vez
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(movements.router, prefix="/api/movements", tags=["movements"])

@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    print(f"{'='*60}")
    print(f"🚀 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Iniciando Mini Inventory API...")
    print(f"{'='*60}")
    
    # Inicializar conexión a MongoDB
    connected = await init_db()
    
    if connected:
        print("✅ Aplicación lista en: http://127.0.0.1:8000")
        print("📚 Documentación: http://127.0.0.1:8000/docs")
    else:
        print("⚠️  Aplicación iniciada SIN conexión a base de datos")
    
    print(f"{'='*60}")

@app.get("/")
async def root():
    """Endpoint raíz - Información de la API"""
    return {
        "message": "¡Bienvenido a Mini Inventory API!",
        "version": "1.0.0",
        "description": "API REST para gestión de inventario",
        "endpoints": {
            "products": {
                "create": "POST /api/products/",
                "list": "GET /api/products/",
                "get": "GET /api/products/{id}",
                "update": "PATCH /api/products/{id}",
                "delete": "DELETE /api/products/{id}"
            },
            "movements": {
                "create": "POST /api/movements/",
                "get_by_product": "GET /api/movements/{product_id}"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar estado del servicio"""
    return {
        "status": "healthy",
        "service": "Mini Inventory API",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

