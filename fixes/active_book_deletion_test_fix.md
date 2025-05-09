# Active Book Deletion Test Fix

## Issue

The test `test_delete_book_with_transactions` in `backend/tests/test_books.py` was failing with a 400 BAD REQUEST error when attempting to delete a book with transactions.

### Error Details
```
assert 400 == 200
where 400 = <WrapperTestResponse streamed [400 BAD REQUEST]>.status_code
```

### Root Cause
The test was trying to delete `book1`, but `book1` was set as the active book for the user in the `books` fixture:

```python
# From the books fixture
# Set the first book as active
user_obj.active_book_id = book1.id
db.session.commit()
```

In the `delete_book` endpoint, there's a check that prevents deleting the active book:

```python
# Check if it's the active book
user = g.current_user
is_active = user.active_book_id == book_id

# Prevent deletion of active book
if is_active:
    return (
        jsonify(
            {
                "error": "Cannot delete the active book. Please set another book as active first."
            }
        ),
        400,
    )
```

## Solution

The solution was to first set `book2` as the active book before attempting to delete `book1`. This prevents the 400 error from the API endpoint.

```python
# Set book2 as active before deleting book1 to avoid 400 error
set_active_response = client.post(
    f"/api/v1/books/{book2.id}/set-active",
    headers={"Authorization": f"Bearer {token}"},
)
assert set_active_response.status_code == 200
```

This change ensures that the test properly tests the cascade deletion of transactions when a book is deleted, without violating the application's business logic that prevents deletion of the active book. 