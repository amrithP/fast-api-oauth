
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel  #for data validation .

app = FastAPI()

@app.get("/")
def get_root():
    return{"message":"hello"}

@app.get("/about")
def get_message():
    return{"message":"Hello Sam"}

"""#path parameter is dynamic data in url.   Query parameter after ?
@app.get("/about/{name}")
def get_message_by_name(name:str,age:int):
    return {"message":f"Hi,{name}.You are {age} years old."}

@app.get("/aboutOptional/{name}")
def get_optional(name:str,age:Optional[int] = None):
    return {"message":f"Hi,{name}.You are {age} years old."}"""

# 2 query parameters
@app.get("/about/")
def get_queries(name:str,age:Optional[int] = None):
      return {"message":f"Hi,{name}.You are {age} years old."}

class Student(BaseModel):
     name:str
     age:int
     roll:int

@app.post("/create")
def create(student:Student):
     return{
          "name":student.name,
          "age": student.age,
          "roll": student.roll
     }