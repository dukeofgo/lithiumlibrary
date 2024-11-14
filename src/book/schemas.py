from pydantic import BaseModel
from datetime import date

"""class inherits from BookBase will also inherit the Config"""
class BookBase(BaseModel):
    title: str
    author: str | None
    isbn: str 

    class Config:
        orm_mode = True

class BookMetadata(BookBase):
    id: int
    added_date: date
    borrowed_date: date | None = None 
    returned_date: date | None = None
    is_borrowed: bool

class BookInfo(BookBase):
    edition: str | None = None
    publisher: str | None = None
    publish_date: str | None = None 
    publish_place: str | None = None
    number_of_pages: int | None = None 
    description: str | None = None
    language: str | None = None 
    lccn: str | None = None 
    subtitle: str | None = None 
    subjects: str | None = None
    cover_image: bytes | None = None
    user_id: int | None = None

#ONLY BOOK WITH ISBN IS ALLOWED TO BE CREATED
class BookCreate(BookBase, BookInfo):
    """    
    title: str
    author: str | None
    isbn: str 
    edition: str | None = None
    publisher: str | None = None
    publish_date: str | None = None 
    publish_place: str | None = None
    number_of_pages: int | None = None 
    description: str | None = None
    language: str | None = None 
    lccn: str | None = None 
    subtitle: str | None = None 
    subjects: str | None = None
    cover_image: bytes | None = None
    user_id: int | None = None 
    """
    pass
class BookUpdate(BookBase, BookInfo):
    """    
    title: str
    author: str | None
    isbn: str
    edition: str | None = None
    publisher: str | None = None
    publish_date: str | None = None 
    publish_place: str | None = None
    number_of_pages: int | None = None 
    description: str | None = None
    language: str | None = None 
    lccn: str | None = None 
    subtitle: str | None = None 
    subjects: str | None = None
    cover_image: bytes | None = None
    user_id: int | None = None 
    """
    pass



