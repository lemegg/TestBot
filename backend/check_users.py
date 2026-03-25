from app.db import SessionLocal
from app.models.models import User
import json

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        result = []
        for u in users:
            result.append({
                "id": u.id,
                "email": u.email,
                "company": u.company_name,
                "role": u.role
            })
        print(json.dumps(result, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
