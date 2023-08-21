from fastapi import APIRouter, Depends, status, HTTPException,Request
from fastapi.security import OAuth2PasswordRequestForm
from security import jwttoken
from config.db import validate_db
from security.hashing import Hash

router = APIRouter(tags=['Authentication'])

@router.post('/login')
def login(req: Request,request:OAuth2PasswordRequestForm = Depends(),conn=Depends(validate_db)):
    if req.headers.get("db-status") == "Down":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Down")
    mybook=conn["BookDB"]
    authors = mybook.authors.find_one({"email": request.username})
    if authors == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Incorrect email")
    if not Hash.verify(authors["password"], request.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Incorrect password")

    access_token = jwttoken.create_access_token(data={"sub": authors["email"],"id": str(authors["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}