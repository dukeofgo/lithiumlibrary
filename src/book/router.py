import json

import httpx
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from ..auth import dependencies
from ..database import get_db
from . import crud as crud_books, schemas
from ..user import crud as crud_users

router = APIRouter(
    prefix = "/books",
)

TIMEOUT = 15.0

@router.post(
    "/create",
    response_model=schemas.BookCreate,
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["admin", "superuser"])
    ])
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    if crud_books.get_book_by_isbn(isbn=book.isbn, db=db):
        raise HTTPException(status_code=400, detail="Book already exist")  

    return crud_books.create_book(book=book, db=db)

@router.post(
    "/create/{isbn}", 
    response_model=schemas.BookCreate,
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["admin", "superuser"])
    ])
async def create_book_by_isbn(isbn: str, db: Session = Depends(get_db)):

    OPENLIB_URL = f"http://openlibrary.org/api/volumes/brief/isbn/{isbn}.json"
    
    #request data from external API
    async with httpx.AsyncClient() as client:
        try:
            book_response = await client.get(OPENLIB_URL, timeout=TIMEOUT)

        except httpx.ReadTimeout:
            raise HTTPException(status_code=400, detail= "Request Time Out") 
        except httpx.RequestError:
            raise HTTPException(status_code=400, detail= "Request Error")
        
    #retrieve json data from HTTP response object
    json_content = book_response.json()
    #convert json data to python dict
    dict_content = json.loads(json_content)

    OPENLIB_KEY = list(dict_content['records'].keys())

    #select certain book keys
    selected_keys = {
        'title': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('data', {}).get('title', None),
        'author': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('data', {}).get('authors', [{}])[0].get('name', None),
        'edition': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('details', {}).get('details', {}).get('edition_name', None),
        'publisher': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('data', {}).get('publishers', [{}])[0].get('name', None),
        'publish_date': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('publishDates', [None])[0],
        'publish_place': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('data', {}).get('publish_places', [{}])[0].get('name', None),
        'number_of_pages': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('data', {}).get('number_of_pages', None),
        'description': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('details', {}).get('details', {}).get('description', {}).get('value', None),
        'language': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('details', {}).get('details', {}).get('languages', [{}])[0].get('key', None),
        'isbn': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('isbns', [None])[0],
        'lccn': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('data', {}).get('identifiers', {}).get('lccn', None)[0],
        'subtitle': dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('data', {}).get('subtitle', None),
        'subjects':  dict_content.get('records', {}).get(f'{OPENLIB_KEY[0]}', {}).get('details', {}).get('details', {}).get('subjects', None)[0],
}     
    #convert python dict to pydantic object
    book = schemas.BookCreate(**selected_keys)

    return crud_books.create_book(book=book, db=db)

@router.get(
    "/retrieve/{isbn_or_id}", 
    response_model=schemas.Book,
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["user", "admin", "superuser"]), 
        ])
def get_book_by_isbn_id(isbn_or_id: str, db: Session = Depends(get_db)):
    db_book = crud_books.get_book_by_isbn_or_id(isbn_or_id=isbn_or_id, db=db)
    if not db_book:
        raise HTTPException(status_code=400, detail="Book not found")
    return db_book

@router.get(
    "/retrieve/books", 
    response_model=list[schemas.Book],
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["user", "admin", "superuser"]),
    ])
def get_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_books = crud_books.get_books(skip=skip, limit=limit, db=db)
    return db_books

@router.patch(
    "/update/{book_id}", 
    response_model=schemas.BookUpdate,
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["admin", "superuser"]),
    ])
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    db_book = crud_books.get_book_by_id(book_id=book_id, db=db)
    if not db_book:
        raise HTTPException(status_code=400, detail="Book not found")
    return crud_books.update_book(book_id=book_id, book=book, db=db)

@router.delete(
    "/delete/{book_id}",
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["user", "admin", "superuser"]), 
    ])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud_books.get_book_by_id(book_id=book_id, db=db)
    if not db_book:
        HTTPException(status_code=400, detail="Target book does not exist")
    return crud_books.delete_book(book_id=book_id, db=db)


@router.patch(
    "/borrow/",
    response_model=schemas.BookUpdate,
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["user", "admin", "superuser"]), 
    ])
def borrow_book(email: str, book_id: int, db: Session = Depends(get_db)):
    db_user = crud_users.get_user_by_email(email=email, db=db)
    db_book = crud_books.get_book_by_id(book_id=book_id, db=db)
    
    if not (db_user or db_book):
        raise HTTPException(status_code=400, detail="Target user and book do not exist")
    if db_book.is_borrowed:
        raise HTTPException(status_code=400, detail="Book is already borrowed by another user")
    
    db_book.borrow(db_user)

    return crud_books.update_book(book_id=book_id, book=db_book, db=db)
    
@router.patch(
    "/return/",
    response_model=schemas.BookUpdate,
    dependencies=[
        Security(dependencies.authorize_current_user, scopes=["user", "admin", "superuser"]), 
    ])
def return_book(email: str, book_id: int, db: Session = Depends(get_db)):
    db_user = crud_users.get_user_by_email(email=email, db=db)
    db_book = crud_books.get_book_by_id(book_id=book_id, db=db)
    
    if not (db_user or db_book):
        raise HTTPException(status_code=400, detail="Target user and book do not exist")
    if not db_book.is_borrowed:
        raise HTTPException(status_code=400, detail="Target book has not been borrowed")
    if db_book.loan_to_user != email:
         raise HTTPException(status_code=400, detail="User did not borrow this specific book")
    
    db_book.return_book()
     
    return crud_books.update_book(book_id=book_id, book=db_book, db=db)