from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from . import schemas, models

def get_book_by_id(db: Session, book_id: int):
    return db.execute(select(models.Book).where(models.Book.id == book_id)).scalars().first()

def get_book_by_isbn(db: Session, isbn: int):   
    return db.execute(select(models.Book).where(models.Book.isbn == isbn)).scalars().first()

def get_book_by_isbn_or_id(db: Session, isbn_or_id: str):
    return db.execute(select(models.Book).where(or_(models.Book.isbn == isbn_or_id, models.Book.id == isbn_or_id))).scalars().first()

def get_books(db: Session, skip: int = 0, limit: int = 20):
    return db.execute(select(models.Book).offset(skip).limit(limit).all())

def create_book(db: Session, book: schemas.BookCreate):
    #convert pydantic model to python dict
    book_dict = book.model_dump(exclude_unset=True)
    #unpack book_dict into model
    db_book = models.Book(**book_dict)

    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book

def update_book(db: Session, book_id: int, book: schemas.BookUpdate):
    db_book = get_book_by_id(db=db, book_id=book_id)
    update_data = book.model_dump(exclude_unset=True)

    """If fields have been modified, setattr, if not then skip setattr"""
    if update_data:
        for key, value in update_data.items():
            setattr(db_book, key, value)

    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book

def delete_book(db: Session, book_id: int):
    db_book = get_book_by_id(db=db, book_id=book_id)

    db.delete(db_book)
    db.commit()

    return {"message": "Book deleted successfully"}