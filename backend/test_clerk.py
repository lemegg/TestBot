import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
USER_ID = "user_3AkfvSsOZ1opHSb5SfStJkGdhiS"

def test_clerk_api():
    print(f"Testing Clerk API for user: {USER_ID}")
    print(f"Key used: {CLERK_SECRET_KEY[:10]}...")
    
    headers = {"Authorization": f"Bearer {CLERK_SECRET_KEY}"}
    url = f"https://api.clerk.com/v1/users/{USER_ID}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.ok:
            data = response.json()
            email_addresses = data.get("email_addresses", [])
            primary_email_id = data.get("primary_email_address_id")
            
            email = None
            for email_obj in email_addresses:
                if email_obj.get("id") == primary_email_id:
                    email = email_obj.get("email_address")
                    break
            
            if not email and email_addresses:
                email = email_addresses[0].get("email_address")
            
            if email:
                print(f"Syncing email to DB: {email}")
                from app.db import SessionLocal
                from app.models.models import User
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == USER_ID).first()
                    if user:
                        user.email = email
                        db.commit()
                        print("Successfully updated database!")
                    else:
                        print("User not found in DB")
                finally:
                    db.close()
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_clerk_api()
