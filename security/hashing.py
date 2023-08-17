from passlib.context import CryptContext

pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash():
    def bcrypt(password: str):
        return pass_context.hash(password)

    def verify(hashed_password,plain_password):
        return pass_context.verify(plain_password,hashed_password)