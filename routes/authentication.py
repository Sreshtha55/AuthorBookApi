from fastapi import APIRouter, Depends, status, HTTPException,Request
from fastapi.security import OAuth2PasswordRequestForm
from security import jwttoken
from config.db import validate_db
from security.hashing import Hash
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

router = APIRouter(tags=['Authentication'])

@router.post('/login')
def login(req: Request,request:OAuth2PasswordRequestForm = Depends(),conn=Depends(validate_db)):
    logger.info(f"Login Request received!")
    if req.headers.get("db-status") == "Down":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Down")
    mybook=conn["BookDB"]
    logger.info(f"Request email is {request.username}")
    authors = mybook.authors.find_one({"email": request.username})
    logger.info(f"Checking this email {request.username} in DB")
    if authors == None:
        logger.error(f"No email with this id {request.username} found in DB")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Incorrect email")
    logger.info(f"Matching the password with the password stored in DB")
    if not Hash.verify(authors["password"], request.password):
        logger.error(f"Password didn't matched!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Incorrect password")
    logger.info(f"Username and password matches in DB")
    logger.info(f"Creating access token")
    access_token = jwttoken.create_access_token(data={"sub": authors["email"],"id": str(authors["_id"])})
    logger.info(f"Access token Created and sent in response")
    return {"access_token": access_token, "token_type": "bearer"}