""" get les secrets du fichier .env : python scripts/generate_secrets.py"""

import secrets

from cryptography.fernet import Fernet

print(f"JWT_SECRET={secrets.token_urlsafe(48)}")
print(f"API_KEY_PEPPER={secrets.token_urlsafe(48)}")
print(f"DATA_ENCRYPTION_KEYS={Fernet.generate_key().decode()}")
