from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
