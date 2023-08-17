from fastapi import APIRouter,Depends,status
from security import oauth2
from models import bookmodel
from repository import book_repository

router = APIRouter(prefix="/book",tags=['Book'])

@router.post('/',status_code=status.HTTP_201_CREATED)
def create(request: bookmodel.Book, current_user: bookmodel.Author = Depends(oauth2.get_current_user)):
    current_user_email = current_user.email
    return book_repository.create(request,current_user_email)

@router.get('/',status_code=status.HTTP_200_OK)
def show(current_user: bookmodel.Author = Depends(oauth2.get_current_user), search: str | None=None, limit: int | None=None):
    current_user_email = current_user.email
    return book_repository.show_all(current_user_email,search,limit)

@router.get('/{title}', status_code=status.HTTP_200_OK)
def show(title: str, current_user: bookmodel.Author = Depends(oauth2.get_current_user)):
    return book_repository.show_by_title(title)


@router.patch('/{id}',status_code=status.HTTP_200_OK)
def patch(id:str, request: bookmodel.UpdateBook, current_user: bookmodel.Author = Depends(oauth2.get_current_user)):
    current_user_email = current_user.email
    return book_repository.patch(id,request,current_user_email)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(id: str, current_user: bookmodel.Author = Depends(oauth2.get_current_user)):
    current_user_email = current_user.email
    return book_repository.delete(id,current_user_email)

