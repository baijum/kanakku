from typing import List, Optional

from flask import current_app

from app.extensions import db
from app.models import Book, User


class BookNotFoundError(Exception):
    """Exception raised when a book is not found."""


class BookService:
    """Service layer for book operations."""

    @staticmethod
    def get_user_books(user_id: int) -> List[Book]:
        """Get all books for a specific user."""
        current_app.logger.debug(f"Getting books for user {user_id}")
        return Book.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_book_by_id(book_id: int, user_id: int) -> Optional[Book]:
        """Get a specific book by ID for a user."""
        current_app.logger.debug(f"Getting book {book_id} for user {user_id}")
        return Book.query.filter_by(id=book_id, user_id=user_id).first()

    @staticmethod
    def create_book(user_id: int, name: str) -> Book:
        """Create a new book for a user."""
        current_app.logger.debug(f"Creating book '{name}' for user {user_id}")

        # Check if book with the same name already exists for this user
        existing = Book.query.filter_by(user_id=user_id, name=name).first()
        if existing:
            raise ValueError("Book with this name already exists")

        # Create the book
        book = Book(user_id=user_id, name=name)
        db.session.add(book)
        db.session.commit()

        current_app.logger.info(
            f"Created book '{name}' with ID {book.id} for user {user_id}"
        )
        return book

    @staticmethod
    def update_book(book_id: int, user_id: int, name: str) -> Book:
        """Update a book's name."""
        current_app.logger.debug(f"Updating book {book_id} for user {user_id}")

        book = Book.query.filter_by(id=book_id, user_id=user_id).first()
        if not book:
            raise BookNotFoundError("Book not found")

        # Check if name is unique for user (excluding current book)
        existing = Book.query.filter(
            Book.user_id == user_id,
            Book.name == name,
            Book.id != book_id,
        ).first()

        if existing:
            raise ValueError("Book with this name already exists")

        book.name = name
        db.session.commit()

        current_app.logger.info(f"Updated book {book_id} name to '{name}'")
        return book

    @staticmethod
    def set_active_book(book_id: int, user_id: int) -> Book:
        """Set a book as active for a user."""
        current_app.logger.debug(f"Setting book {book_id} as active for user {user_id}")

        # Make sure book exists and belongs to user
        book = Book.query.filter_by(id=book_id, user_id=user_id).first()
        if not book:
            raise BookNotFoundError("Book not found")

        # Update user's active book
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        user.active_book_id = book.id
        db.session.commit()

        current_app.logger.info(
            f"Set book '{book.name}' (ID: {book.id}) as active for user {user_id}"
        )
        return book

    @staticmethod
    def get_active_book(user_id: int) -> Optional[Book]:
        """Get the active book for a user."""
        current_app.logger.debug(f"Getting active book for user {user_id}")

        user = db.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        active_book_id = user.active_book_id

        # Check if active_book_id is set on the user object
        if not active_book_id:
            current_app.logger.warning(f"User {user_id} has no active_book_id set")
            return None

        # Fetch the book using the ID
        current_app.logger.debug(
            f"Fetching active book with ID: {active_book_id} for user {user_id}"
        )
        active_book = db.session.get(Book, active_book_id)

        # Verify the fetched book belongs to the user and exists
        if not active_book:
            current_app.logger.error(
                f"Active book ID {active_book_id} (from user.active_book_id) not found in Book table for user {user_id}"
            )
            return None
        elif active_book.user_id != user_id:
            current_app.logger.error(
                f"Active book ID {active_book_id} belongs to user {active_book.user_id}, not the current user {user_id}"
            )
            # This case indicates a data integrity issue. Clear the invalid ID.
            user.active_book_id = None
            db.session.commit()
            return None

        current_app.logger.debug(
            f"Successfully found active book: {active_book.name} (ID: {active_book.id})"
        )
        return active_book

    @staticmethod
    def delete_book(book_id: int, user_id: int) -> None:
        """Delete a book and all its associated accounts and transactions."""
        current_app.logger.debug(f"Deleting book {book_id} for user {user_id}")

        # Make sure book exists and belongs to user
        book = Book.query.filter_by(id=book_id, user_id=user_id).first()
        if not book:
            # Use a custom exception to indicate not found (should return 404)
            raise BookNotFoundError("Book not found")

        # Check if it's the active book
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        is_active = user.active_book_id == book_id

        # Prevent deletion of active book
        if is_active:
            raise ValueError(
                "Cannot delete the active book. Please set another book as active first."
            )

        # Delete book (associated accounts and transactions will be deleted via cascade)
        db.session.delete(book)
        db.session.commit()

        current_app.logger.info(
            f"Deleted book '{book.name}' (ID: {book_id}) for user {user_id}"
        )
