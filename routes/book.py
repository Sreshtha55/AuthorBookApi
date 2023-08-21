from fastapi import APIRouter,Depends,status,Request,HTTPException
from security import oauth2
from models import bookmodel
from repository import book_repository
from config.db import validate_db

router = APIRouter(prefix="/book",tags=['Book'])

@router.post('/',status_code=status.HTTP_201_CREATED)
def create(req:Request,request: bookmodel.Book, current_user: bookmodel.Author = Depends(oauth2.get_current_user),conn=Depends(validate_db)):
    if req.headers.get("db-status") == "Down":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Down")
    current_user_dict = {"email":current_user.email,"id":current_user.id}
    return book_repository.create(request,current_user_dict,conn)

@router.get('/',status_code=status.HTTP_200_OK)
def show_all(req:Request,conn=Depends(validate_db),current_user: bookmodel.Author = Depends(oauth2.get_current_user), search: str | None=None, limit: int | None=None):
    if req.headers.get("db-status") == "Down":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Down")
    current_user_id = current_user.id
    return book_repository.show_all(conn,current_user_id,search,limit)

@router.get('/{title}',status_code=status.HTTP_200_OK)
def show_by_title(req:Request,title: str, current_user: bookmodel.Author = Depends(oauth2.get_current_user),conn=Depends(validate_db)):
    if req.headers.get("db-status") == "Down":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Down")
    return book_repository.show_by_title(title,conn)


@router.patch('/{id}',response_model=bookmodel.Book,status_code=status.HTTP_200_OK)
def patch(req:Request,id:str, request: bookmodel.UpdateBook, current_user: bookmodel.Author = Depends(oauth2.get_current_user),conn=Depends(validate_db)):
    if req.headers.get("db-status") == "Down":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Down")
    current_user_id = current_user.id
    return book_repository.patch(id,request,current_user_id,conn)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(req:Request,id: str, current_user: bookmodel.Author = Depends(oauth2.get_current_user),conn=Depends(validate_db)):
    if req.headers.get("db-status") == "Down":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Down")
    current_user_id = current_user.id
    return book_repository.delete(id,current_user_id,conn)

