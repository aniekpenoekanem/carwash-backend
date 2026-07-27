from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

password = "Password123"

hashed = hash_password(password)

print("Hash:", hashed)

print(
    "Verify:",
    verify_password(password, hashed),
)

token = create_access_token("user@example.com")

print("Token:", token)

print("Decoded:", decode_access_token(token))