from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print(f"Connected to DB: {engine.url.database}")
print("=== Table List ===")
for table in tables:
    print(f"- {table}")

if not tables:
    print("❌ No tables found! 'create_all' might have failed or not run yet.")
else:
    required = ['users', 'user_faces', 'user_health', 'user_allergies', 'menus']
    missing = [t for t in required if t not in tables]
    if missing:
        print(f"⚠️ Missing tables: {missing}")
    else:
        print("✅ All required tables exist.")
