//Part 2: FastAPI
const API_URL = '/api/books';

document.addEventListener('DOMContentLoaded', () => {
    loadBooks();
});


async function loadBooks() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error('Failed to fetch books');
        }

        const books = await response.json();
        displayBooks(books);
    } catch (error) {
        console.error('Error loading books:', error);
        alert('Failed to load books');
    }
}

//display books in table
function displayBooks(books) {
    const tbody = document.getElementById('bookTableBody');
    tbody.innerHTML = '';

    if (books.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center;">No books found</td></tr>';
        return;
    }

    books.forEach(book => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${book.id}</td>
            <td>${book.title}</td>
            <td>${book.author}</td>
        `;
        tbody.appendChild(row);
    });
}

//2.1: Add a new book (2 points)
async function createBook() {
    const titleInput = document.getElementById('createTitle');
    const authorInput = document.getElementById('createAuthor');
    const title = titleInput.value.trim();
    const author = authorInput.value.trim();

    if (!title || !author) {
        alert('Please enter both book title and author name');
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                id: 0,
                title: title,
                author: author 
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create book');
        }

        const newBook = await response.json();
        console.log('Created book:', newBook);

        // redirect to home view
        titleInput.value = '';
        authorInput.value = '';
        await loadBooks();
        alert(`Book "${newBook.title}" by ${newBook.author} added successfully!`);
    } catch (error) {
        console.error('Error creating book:', error);
        alert('Failed to create book: ' + error.message);
    }
}

//2.2: Update the book with ID 1 (2 points)
async function updateBook() {
    const idInput = document.getElementById('updateId');
    const titleInput = document.getElementById('updateTitle');
    const authorInput = document.getElementById('updateAuthor');
    const id = parseInt(idInput.value);
    const title = titleInput.value.trim();
    const author = authorInput.value.trim();

    if (!id || !title || !author) {
        alert('Please enter Book ID, new title, and new author');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                id: id,
                title: title,
                author: author 
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update book');
        }

        const updatedBook = await response.json();
        console.log('Updated book:', updatedBook);

        //redirect to home view
        idInput.value = '';
        titleInput.value = '';
        authorInput.value = '';
        await loadBooks();
        alert(`Book ID ${id} updated to "${updatedBook.title}" by ${updatedBook.author}!`);
    } catch (error) {
        console.error('Error updating book:', error);
        alert('Failed to update book: ' + error.message);
    }
}

//2.3: Delete the book with the highest ID (2 points)
async function deleteHighestIdBook() {
    if (!confirm('Are you sure you want to delete the book with the highest ID?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/highest`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete book');
        }

        const result = await response.json();
        console.log(result.message);

        //redirect to home view
        await loadBooks();
        alert(result.message);
    } catch (error) {
        console.error('Error deleting book:', error);
        alert('Failed to delete book: ' + error.message);
    }
}

//2.4: Search functionality (2 points)
async function searchBooks() {
    const searchInput = document.getElementById('searchTitle');
    const searchTerm = searchInput.value.trim();

    try {
        let url = `${API_URL}/search`;
        if (searchTerm) {
            url += `?title=${encodeURIComponent(searchTerm)}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to search books');
        }

        const books = await response.json();
        displayBooks(books);
        
        if (searchTerm) {
            console.log(`Found ${books.length} book(s) matching "${searchTerm}"`);
        }
    } catch (error) {
        console.error('Error searching books:', error);
        alert('Failed to search books: ' + error.message);
    }
}

async function clearSearch() {
    const searchInput = document.getElementById('searchTitle');
    searchInput.value = '';
    await loadBooks();
}
