from datetime import datetime, timedelta
from jose import JWTError, jwt
from models import bookmodel
from os import environ

import logging
from datetime import  datetime

now=datetime.now()
file_format = now.strftime("%Y-%m-%d-%H")

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler=logging.FileHandler(f"logs/bookapi_{file_format}.log")
formatter=logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(environ['SECRET_KEY']), algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token:str,credentials_exception):
    try:
        payload = jwt.decode(token, environ['SECRET_KEY'], algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        id: str = payload.get("id")
        if email is None:
            logger.error("Login error as the email is not authorized/found")
            raise credentials_exception
        token_data = bookmodel.TokenData(email=email,id=id)
        return token_data
    except JWTError:
        logger.error("Login Error as Invalid token provided")
        raise credentials_exception