from utils import *

password = "hello123"

hashed = hash_password(password)

print("Original:", password)
print("Hash:", hashed)

print(verify_password("hello123", hashed))
print(verify_password("wrong", hashed))