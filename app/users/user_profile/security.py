from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return password_bytes.decode("utf-8", errors="ignore")


def hash_password(password: str) -> str:
    normalized_password = _normalize_password(password)
    return pwd_context.hash(normalized_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    normalized_password = _normalize_password(plain_password)
    return pwd_context.verify(normalized_password, hashed_password)
