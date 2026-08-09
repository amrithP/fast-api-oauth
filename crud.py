from fastapi import FastAPI,status
from pydantic import BaseModel
from fastapi.exceptions import HTTPException

app = FastAPI()

books = [
  {
    "id": 1,
    "title": "The Alchemist",
    "author": "Paulo Coelho",
    "publish_date": "1988-01-01"
  },
  {
    "id": 2,
    "title": "The God of Small Things",
    "author": "Arundhati Roy",
    "publish_date": "1997-04-04"
  },
  {
    "id": 3,
    "title": "The White Tiger",
    "author": "Aravind Adiga",
    "publish_date": "2008-01-01"
  },
  {
    "id": 4,
    "title": "The Palace of Illusions",
    "author": "Chitra Banerjee Divakaruni",
    "publish_date": "2008-02-12"
  }
]

@app.get("/books")
def get_books():
    return books

@app.get("/books/{book_id}")
def get_books_id(book_id:int):
    for book in books:
        if book['id']==book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="id not matched")

        


#pydantic class for post 
class Book(BaseModel):
    id:int
    title:str
    author:str
    publish_date:str

#book is a pydantic object . So to convert into dictionary , we use model_dump()
@app.post("/books")
def create_book(book:Book):
    new_book = book.model_dump()
    books.append(new_book)
    return {"message":"successfully posted"}


#pydantic class for put.   no nned for id 

class Book_Update(BaseModel):
    title:str
    author:str
    publish_date:str

@app.put("/books/{book_id}")
def update_books(book_id:int,book_update:Book_Update):
    for book in books:
        if book["id"] ==book_id:
            book["title"] = book_update.title
            book["author"] = book_update.author
            book["publish_date"] = book_update.publish_date
            return {"message":"successfully updated"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ID is not matched")

@app.delete("/books/{book_id}")
def delete_books(book_id:int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return{"message":"deleted successfully"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="id not matched ")


 