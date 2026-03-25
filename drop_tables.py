from sqlalchemy import text
from app.db import engine
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

def drop_all_cascade():
    print("Dropping all tables with CASCADE...")
    with engine.connect() as conn:
        # Get all table names
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        
        for table in tables:
            print(f"Dropping table {table} CASCADE...")
            conn.execute(text(f"DROP TABLE IF EXISTS \"{table}\" CASCADE"))
        
        conn.commit()
    print("All tables dropped successfully.")

if __name__ == "__main__":
    drop_all_cascade()
