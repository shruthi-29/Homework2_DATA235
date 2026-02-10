# Part 2: FastAPI (8 points)
# Book Management REST API

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI()

# Book model
class Book(BaseModel):
    id: int
    title: str
    author: str

# In-memory database
books_db: List[Book] = [
    Book(id=1, title="Wuthering Heights", author="Emily Bronte"),
    Book(id=2, title="Pride and Prejudic", author="Jane Austen"),
    Book(id=3, title="Anne of Green Gables", author="Lucy Maud Montgomery"),
]

# Counter for generating new IDs
next_id = 4


# Serve the main HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        html_path = os.path.join("static", "html", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="index.html not found")


# Get all books
@app.get("/api/books", response_model=List[Book])
async def get_books():
    return books_db


# Part 2.1: Add a new book (2 points)
# The user should be able to enter the Book Title and Author Name.
# Once submitted, the book should be added, and the user should be redirected 
# to the home view showing the updated list of books.
@app.post("/api/books", response_model=Book)
async def create_book(book: Book):
    global next_id
    # Create new book with auto-generated ID
    new_book = Book(
        id=next_id,
        title=book.title,
        author=book.author
    )
    books_db.append(new_book)
    next_id += 1
    print(f"Book added: {new_book}")
    return new_book


# Part 2.2: Update the book with ID 1 (2 points)
# Update book with ID 1 to title: "Harry Potter", Author Name: "J.K Rowling"
# After submitting the data, redirect to the home view and show the updated data
@app.put("/api/books/{book_id}", response_model=Book)
async def update_book(book_id: int, book: Book):
    for idx, existing_book in enumerate(books_db):
        if existing_book.id == book_id:
            # Update the book
            updated_book = Book(
                id=book_id,
                title=book.title,
                author=book.author
            )
            books_db[idx] = updated_book
            print(f"Book updated: {updated_book}")
            return updated_book
    
    raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")


# Part 2.3: Delete the book with the highest ID (2 points)
# After submitting the data, redirect to the home view and show the updated data
@app.delete("/api/books/highest")
async def delete_highest_id_book():
    if not books_db:
        raise HTTPException(status_code=404, detail="No books available to delete")
    
    # Find the book with the highest ID
    highest_book = max(books_db, key=lambda book: book.id)
    books_db.remove(highest_book)
    print(f"Book deleted: {highest_book}")
    
    return {"message": f"Book with ID {highest_book.id} ('{highest_book.title}') deleted successfully"}


# Part 2.4: Search functionality (2 points)
# The user should be able to search for a book by name/title
# When the user enters a name and searches, the list should update to show only matching books
@app.get("/api/books/search", response_model=List[Book])
async def search_books(title: Optional[str] = None):
    if not title:
        return books_db
    
    # Filter books by title (case-insensitive partial match)
    search_term = title.lower()
    matching_books = [
        book for book in books_db 
        if search_term in book.title.lower()
    ]
    
    return matching_books


# Mount static files AFTER defining all routes
app.mount("/static", StaticFiles(directory="static"), name="static")


# Run with: uvicorn main:app --reload --port 8001
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)