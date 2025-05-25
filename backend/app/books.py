from flask import Blueprint, current_app, g, jsonify, request

from app.models import Book, db

from .extensions import api_token_required

books = Blueprint("books", __name__)


@books.route("/api/v1/books", methods=["GET"])
@api_token_required
def get_books():
    """Get all books for the current user."""
    current_app.logger.debug("Entered get_books route")

    books_list = Book.query.filter_by(user_id=g.current_user.id).all()

    return jsonify([book.to_dict() for book in books_list])


@books.route("/api/v1/books", methods=["POST"])
@api_token_required
def create_book():
    """Create a new book."""
    current_app.logger.debug("Entered create_book route")

    data = request.get_json()

    if "name" not in data:
        return jsonify({"error": "Missing required field: name"}), 400

    # Use g.current_user
    user_id = g.current_user.id

    # Check if book with the same name already exists for this user
    existing = Book.query.filter_by(user_id=user_id, name=data["name"]).first()
    if existing:
        return jsonify({"error": "Book with this name already exists"}), 400

    # Create the book
    book = Book(user_id=user_id, name=data["name"])

    db.session.add(book)
    db.session.commit()

    return (
        jsonify({"message": "Book created successfully", "book": book.to_dict()}),
        201,
    )


@books.route("/api/v1/books/<int:book_id>", methods=["GET"])
@api_token_required
def get_book(book_id):
    """Get a specific book."""
    current_app.logger.debug(f"Entered get_book route for ID: {book_id}")

    # Use g.current_user
    book = Book.query.filter_by(id=book_id, user_id=g.current_user.id).first_or_404()

    return jsonify(book.to_dict())


@books.route("/api/v1/books/<int:book_id>", methods=["PUT"])
@api_token_required
def update_book(book_id):
    """Update a book."""
    current_app.logger.debug(f"Entered update_book route for ID: {book_id}")

    data = request.get_json()

    # Use g.current_user
    book = Book.query.filter_by(id=book_id, user_id=g.current_user.id).first_or_404()

    if "name" in data:
        # Check if name is unique for user
        existing = Book.query.filter(
            Book.user_id == g.current_user.id,
            Book.name == data["name"],
            Book.id != book_id,
        ).first()

        if existing:
            return jsonify({"error": "Book with this name already exists"}), 400

        book.name = data["name"]

    db.session.commit()

    return jsonify({"message": "Book updated successfully", "book": book.to_dict()})


@books.route("/api/v1/books/<int:book_id>/set-active", methods=["POST"])
@api_token_required
def set_active_book(book_id):
    """Set a book as active for the current user."""
    current_app.logger.debug(f"Entered set_active_book route for ID: {book_id}")

    # Make sure book exists and belongs to user
    book = Book.query.filter_by(id=book_id, user_id=g.current_user.id).first_or_404()

    # Update user's active book
    user = g.current_user
    user.active_book_id = book.id
    db.session.commit()

    return jsonify(
        {"message": f"Book '{book.name}' set as active", "active_book": book.to_dict()}
    )


@books.route("/api/v1/books/active", methods=["GET"])
@api_token_required
def get_active_book():
    """Get the current user's active book."""
    current_app.logger.debug("Entered get_active_book route")

    user = g.current_user
    active_book_id = user.active_book_id

    # Check if active_book_id is set on the user object
    if not active_book_id:
        current_app.logger.warning(
            f"User {user.id} has no active_book_id set. Returning empty."
        )
        return jsonify({})  # Active book is not set

    # Fetch the book using the ID
    current_app.logger.debug(
        f"Fetching active book with ID: {active_book_id} for user {user.id}"
    )
    active_book = db.session.get(Book, active_book_id)

    # Verify the fetched book belongs to the user and exists
    if not active_book:
        current_app.logger.error(
            f"Active book ID {active_book_id} (from user.active_book_id) not found in Book table for user {user.id}"
        )
        return jsonify({})  # Book not found
    elif active_book.user_id != user.id:
        current_app.logger.error(
            f"Active book ID {active_book_id} belongs to user {active_book.user_id}, not the current user {user.id}"
        )
        # This case indicates a data integrity issue. Clear the invalid ID.
        user.active_book_id = None
        db.session.commit()
        return jsonify({})  # Return empty as the ID was invalid

    current_app.logger.debug(
        f"Successfully found active book: {active_book.name} (ID: {active_book.id})"
    )
    return jsonify(active_book.to_dict())


@books.route("/api/v1/books/<int:book_id>", methods=["DELETE"])
@api_token_required
def delete_book(book_id):
    """Delete a book and all its associated accounts and transactions."""
    current_app.logger.debug(f"Entered delete_book route for ID: {book_id}")

    # Make sure book exists and belongs to user
    book = Book.query.filter_by(id=book_id, user_id=g.current_user.id).first_or_404()

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

    # Delete book (associated accounts and transactions will be deleted via cascade)
    db.session.delete(book)

    db.session.commit()

    return jsonify({"message": "Book and all associated accounts deleted successfully"})
