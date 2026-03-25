from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_database():
    engine = create_engine(settings.DATABASE_URL)
    print("Connecting to database to fix schema...")
    
    with engine.connect() as conn:
        # We need to drop these tables because of the ID type change (Int -> String)
        # In production, we would use migrations, but for setup, dropping is safer.
        print("Dropping problematic tables...")
        conn.execute(text("DROP TABLE IF EXISTS query_feedback CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS query_logs CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS chunks CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS documents CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.commit()
    
    print("Tables dropped. Restarting the backend will recreate them with correct types.")

if __name__ == "__main__":
    fix_database()
