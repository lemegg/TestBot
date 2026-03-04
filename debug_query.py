import requests
import json

BASE_URL = "http://127.0.0.1:8000"
EMAIL = "anurag@theaffordableorganicstore.com"
PASSWORD = "password123"

def debug_query():
    print("Logging in...")
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": EMAIL, "password": PASSWORD})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    query = "how to handle missing tickets"
    print(f"Querying: {query}")
    chat_res = requests.post(
        f"{BASE_URL}/api/chat", 
        headers=headers, 
        json={"query": query}
    )
    print(f"Status: {chat_res.status_code}")
    print(f"Response: {json.dumps(chat_res.json(), indent=2)}")

if __name__ == "__main__":
    debug_query()
