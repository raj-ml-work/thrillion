from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field 
import uvicorn

import datamodel.models as models
from datamodel.database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(bind=engine)


class Book(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=6)


Books = []

@app.get('/')
def hello_api():
    return {'msg': 'success'}

@app.get('/books')
def read_api(db: Session = Depends(get_db)):
    return db.query(models.Books).all()


@app.post('/books')
def create_api(book: Book, db: Session = Depends(get_db)):
    book_model = models.Books()
    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating

    db.add(book_model)
    db.commit()

    return book



@app.put('/books/{book_id}')
def update_api(book_id: int, updated_book: Book, db: Session = Depends(get_db)):
    counter = 0

    book_model = db.query(models.Books).filter(models.Books.id == book_id).first()

    if not book_model:
        raise HTTPException(
            status_code=404,
            detail = f'{book_id}: doesnot exist'
        )
    
    book_model.title = updated_book.title
    book_model.author = updated_book.author
    book_model.description = updated_book.description
    book_model.rating = updated_book.rating

    db.add(book_model)
    db.commit()

    return updated_book


@app.delete('/books/{book_id}')
def delete_api(book_id: int, db: Session = Depends(get_db)):
 
    book_model = db.query(models.Books).filter(models.Books.id == book_id).first()

    if not book_model:
        raise HTTPException(
            status_code=404,
            detail = f'{book_id} doesnot exist'
        )

    db.query(models.Books).filter(models.Books.id == book_id).delete()
    db.commit()

    return {'msg': f'Successfully deleted Book with Id: {book_id}'}


# for debug purpose

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)