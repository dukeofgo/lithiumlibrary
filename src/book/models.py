from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .. database import Base
from .. user import models, schemas
import datetime

class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    title: Mapped[str] = mapped_column(String(64))
    author: Mapped[str] = mapped_column(String(64))
    isbn: Mapped[str] = mapped_column(String(13))
    edition: Mapped[str] = mapped_column(String(64), nullable=True)
    publisher: Mapped[str] = mapped_column(String(64), nullable=True)
    publish_date: Mapped[str] = mapped_column(String(64), nullable=True)
    publish_place: Mapped[str] = mapped_column(String(64), nullable=True)
    number_of_pages: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    language: Mapped[str] = mapped_column(String(32), nullable=True)
    lccn: Mapped[str] = mapped_column(String(64), nullable=True)
    subtitle: Mapped[str] = mapped_column(String(1024), nullable=True)
    subjects: Mapped[str] = mapped_column(String(256), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), nullable=True)
    loan_to_user: Mapped[models.User] = relationship(back_populates="borrowed_books") #implement delete cascade later

    added_date: Mapped[Date] = mapped_column(default=Date.today)
    borrowed_date: Mapped[Date] = mapped_column(nullable=True)
    returned_date: Mapped[Date] = mapped_column(nullable=True)
    
    is_borrowed: Mapped[Boolean] = mapped_column(default=False)

    def borrow(self, user: schemas.User):
        self.loan_to_user = user.email
        self.borrowed_date = datetime.date.today()
        self.returned_date = None
        self.is_borrowed = True

    def return_book(self):
        self.loan_to_user = None
        self.borrowed_date = None
        self.returned_date = datetime.date.today()
        self.is_borrowed = False