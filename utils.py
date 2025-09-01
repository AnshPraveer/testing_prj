from passlib.context import CryptContext
import re
from pydantic import Field



class PasswordManager:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def hash_password(password: str):
        return PasswordManager.password_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return PasswordManager.password_context.verify(plain_password, hashed_password)

    @staticmethod
    def validate_password(password: str):
        if len(password) < 8 or not all(re.search(p, password) for p in [r'[a-z]', r'[A-Z]', r'\d']):
            return False, "Password must be 8+ chars with upper, lower, and number"
        return True, "Valid"




def password_field():
    return Field(
        min_length=8,
        description="Password must be at least 8 characters with uppercase, lowercase, and number"
    )