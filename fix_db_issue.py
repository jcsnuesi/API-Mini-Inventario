import os

# 1. Actualizar app/repositories/products.py
products_py_path = "app/repositories/products.py"

with open(products_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar db. por get_db().
fixed_content = content.replace('db.products', 'get_db().products')
fixed_content = fixed_content.replace('db.movements', 'get_db().movements')

# Agregar import si no existe
if 'from app.db import get_db' not in fixed_content:
    lines = fixed_content.split('\n')
    for i, line in enumerate(lines):
        if 'from app.db import db' in line:
            lines[i] = 'from app.db import get_db'
            break
        elif 'import' in line and i < 10:
            lines.insert(i+1, 'from app.db import get_db')
            break
    
    fixed_content = '\n'.join(lines)

with open(products_py_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("✅ app/repositories/products.py actualizado")

# 2. Hacer lo mismo para movements.py si existe
movements_py_path = "app/repositories/movements.py"
if os.path.exists(movements_py_path):
    with open(movements_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed_content = content.replace('db.movements', 'get_db().movements')
    fixed_content = fixed_content.replace('db.products', 'get_db().products')
    
    with open(movements_py_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ app/repositories/movements.py actualizado")

# 3. Verificar app/db.py
db_py_path = "app/db.py"
with open(db_py_path, 'r', encoding='utf-8') as f:
    db_content = f.read()

if 'def get_db():' not in db_content:
    print("⚠️  app/db.py no tiene función get_db()")
    print("💡 Usa el código de db.py proporcionado arriba")

print("\n🎯 Pasos manuales necesarios:")
print("1. Copia el código corregido de app/db.py mostrado arriba")
print("2. En app/main.py, asegúrate de llamar a init_db() en startup")
print("3. Reinicia la API: uvicorn app.main:app --reload")