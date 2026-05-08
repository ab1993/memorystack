import os
from cryptography.fernet import Fernet

# Load the key from environment variables
ENCRYPTION_KEY = os.getenv("TELEGRAM_ENCRYPTION_KEY")

def get_cipher():
    if not ENCRYPTION_KEY:
        raise ValueError("TELEGRAM_ENCRYPTION_KEY is missing from .env")
    return Fernet(ENCRYPTION_KEY.encode())

def encrypt_chat_id(raw_id: str) -> str:
    """Encrypts the Telegram ID before saving to DB"""
    cipher = get_cipher()
    return cipher.encrypt(raw_id.encode()).decode()

def decrypt_chat_id(encrypted_id: str) -> str:
    """Decrypts the Telegram ID in memory just before sending a message"""
    cipher = get_cipher()
    return cipher.decrypt(encrypted_id.encode()).decode()