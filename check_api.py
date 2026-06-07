import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000"
TEST_SKU = f"TEST_{int(time.time())}"  # SKU único para pruebas

def print_section(title):
    """Imprime una sección con formato"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def test_health_check():
    """Probar health check"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root_endpoint():
    """Probar endpoint raíz"""
    print_section("2. Endpoint Raíz")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"📊 Message: {data.get('message')}")
        print(f"📊 Version: {data.get('version')}")
        
        # Verificar que los endpoints estén documentados
        endpoints = data.get('endpoints', {})
        if 'products' in endpoints:
            print("✅ Endpoints de productos documentados")
        if 'movements' in endpoints:
            print("✅ Endpoints de movimientos documentados")
            
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_product():
    """Probar creación de producto"""
    print_section("3. Crear Producto")
    
    product_data = {
        "sku": TEST_SKU,
        "name": "Producto de Prueba API",
        "category": "Testing",
        "price": 99.99,
        "stock": 50
    }
    
    print(f"📦 Datos enviados:")
    print(json.dumps(product_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/products/",
            json=product_data,
            timeout=10
        )
        
        print(f"\n📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ¡Producto creado exitosamente!")
            print(f"📊 ID del producto: {result.get('id', 'N/A')}")
            print(f"📊 SKU: {result.get('sku', 'N/A')}")
            print(f"📊 Stock inicial: {result.get('stock', 'N/A')}")
            return result.get('id')
            
        elif response.status_code == 400:
            error_msg = response.json().get('detail', 'Error desconocido')
            print(f"⚠️  Error del cliente: {error_msg}")
            return None
            
        else:
            print(f"❌ Error {response.status_code}:")
            print(response.text[:200])
            return None
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def test_list_products():
    """Probar listado de productos"""
    print_section("4. Listar Productos")
    
    try:
        response = requests.get(f"{BASE_URL}/api/products/", timeout=5)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            items = data.get('items', [])
            
            print(f"📊 Total de productos: {total}")
            print(f"📊 Productos en respuesta: {len(items)}")
            
            if items:
                print("\n📋 Primeros productos:")
                for i, product in enumerate(items[:3], 1):
                    print(f"  {i}. {product.get('name')} (SKU: {product.get('sku')})")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text[:200])
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_movement(product_id):
    """Probar creación de movimiento"""
    if not product_id:
        print("⚠️  No hay product_id, omitiendo prueba de movimiento")
        return False
    
    print_section("5. Crear Movimiento de Entrada")
    
    movement_data = {
        "product_id": product_id,
        "type": "in",
        "qty": 10
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/movements/",
            json=movement_data,
            timeout=10
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ¡Movimiento creado exitosamente!")
            print(f"📊 Tipo: {result.get('type')}")
            print(f"📊 Cantidad: {result.get('qty')}")
            return True
        else:
            error_msg = response.json().get('detail', 'Error desconocido')
            print(f"❌ Error: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_product_by_id(product_id):
    """Probar obtención de producto por ID"""
    if not product_id:
        return False
    
    print_section("6. Obtener Producto por ID")
    
    try:
        response = requests.get(f"{BASE_URL}/api/products/{product_id}", timeout=5)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            product = response.json()
            print("✅ ¡Producto encontrado!")
            print(f"📊 Nombre: {product.get('name')}")
            print(f"📊 SKU: {product.get('sku')}")
            print(f"📊 Stock actual: {product.get('stock')}")
            print(f"📊 Precio: ${product.get('price')}")
            return True
        elif response.status_code == 404:
            print("⚠️  Producto no encontrado")
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_documentation():
    """Verificar documentación"""
    print_section("7. Verificar Documentación")
    
    endpoints_to_check = [
        ("Swagger UI", "/docs"),
        ("ReDoc", "/redoc"),
        ("OpenAPI JSON", "/openapi.json")
    ]
    
    all_ok = True
    for name, endpoint in endpoints_to_check:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Disponible ({len(response.text)} bytes)")
            else:
                print(f"❌ {name}: Error {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_ok = False
    
    return all_ok

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DE LA API")
    print(f"📡 URL Base: {BASE_URL}")
    print(f"🆔 SKU de prueba: {TEST_SKU}")
    
    results = {}
    
    # Ejecutar pruebas en orden
    results['health'] = test_health_check()
    time.sleep(1)
    
    results['root'] = test_root_endpoint()
    time.sleep(1)
    
    results['docs'] = test_documentation()
    time.sleep(1)
    
    product_id = test_create_product()
    results['create'] = bool(product_id)
    time.sleep(1)
    
    if product_id:
        results['get_by_id'] = test_get_product_by_id(product_id)
        time.sleep(1)
        
        results['movement'] = test_create_movement(product_id)
        time.sleep(1)
    
    results['list'] = test_list_products()
    
    # Resumen
    print_section("📊 RESUMEN FINAL")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"✅ Pruebas pasadas: {passed_tests}/{total_tests}")
    print(f"📈 Porcentaje: {passed_tests/total_tests*100:.1f}%")
    
    print("\n📋 Detalle por prueba:")
    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"  {status} - {test_name}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ¡TODAS LAS PRUEBAS PASARON! Tu API está funcionando correctamente.")
        print(f"🌐 Documentación: {BASE_URL}/docs")
        print(f"🛒 Endpoint productos: {BASE_URL}/api/products/")
    else:
        print(f"\n⚠️  Algunas pruebas fallaron. Revisa los mensajes de error.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
        sys.exit(1)