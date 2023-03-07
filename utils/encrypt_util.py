from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash(password: str):
    """
    [summary]: Creates hash of given plain text password
    """
    return pwd_context.hash(password)


def verify_credentials(plain_pwd, hashed_pwd):
    """[Summary]: Validating user credntials
    """
    return pwd_context.verify(plain_pwd, hashed_pwd)