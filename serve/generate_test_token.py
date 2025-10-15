import os
from jose import jwt
from dotenv import load_dotenv

load_dotenv(".env.development")

SECRET_KEY = os.environ.get("LIFE_BOOKSHELF_AI_JWT_SECRET_KEY")
ALGORITHM = "HS256"

payload = {
    "memberId": 1,
    "roles": ["MEMBER"]
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print("\n=== Test JWT Token ===")
print(token)
print("\n=== Use this in Swagger Authorization ===")
print(f"Bearer {token}")
