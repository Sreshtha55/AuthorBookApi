from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from security import jwttoken
from config.db import conn
from security.hashing import Hash

router = APIRouter(tags=['Authentication'])

@router.post('/login')
def login(request:OAuth2PasswordRequestForm = Depends()):
    mybook=conn["BookDB"]
    authors = mybook.authors.find({"email": request.username})
    for author in authors:
        if not author:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid Credentials")
        if not Hash.verify(author["password"], request.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Incorrect password")

        access_token = jwttoken.create_access_token(data={"sub": author["email"]})
        return {"access_token": access_token, "token_type": "bearer"}
#
# @router.post("/logout")
# def user_logout(Authorization: str = Header(None)):
#     oauth2_scheme.revoke_token(Authorization)
#     return {"message": "Token revoked"}