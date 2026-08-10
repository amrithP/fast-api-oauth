from fastapi import FastAPI, Depends
from database import get_db, engine
from sqlalchemy.orm import Session
import model
from pydantic import BaseModel

app = FastAPI()

class Bookstore(BaseModel):
    id: int
    title:str
    author:str
    publish_date:str


@app.post("/books")
def create_book(book: Bookstore, db: Session = Depends(get_db)):
    new_book=model.Book(id=book.id,title=book.title,author=book.author,publish_date=book.publish_date)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get("/books")
def get_books(db:Session = Depends(get_db)):
    new_books=db.query(model.Book).all()
    return new_books


@app.put("/books/{book_id}")
def update_book(book_id: int, book: Bookstore, db: Session = Depends(get_db)):
    existing_book = db.query(model.Book).filter(model.Book.id == book_id).first()

    if existing_book is None:
        return {"message": "Book not found"}

    existing_book.title = book.title
    existing_book.author = book.author
    existing_book.publish_date = book.publish_date

    db.commit()
    db.refresh(existing_book)

    return existing_book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    existing_book = db.query(model.Book).filter(model.Book.id == book_id).first()

    if existing_book is None:
        return {"message": "Book not found"}

    db.delete(existing_book)
    db.commit()

    return {"message": "Book deleted successfully"}

