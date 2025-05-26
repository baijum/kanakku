from flask import Blueprint, current_app, g, jsonify, request
from marshmallow import ValidationError

from app.extensions import api_token_required

from .schemas import CreateBookSchema, UpdateBookSchema
from .services import BookNotFoundError, BookService

books_bp = Blueprint("books", __name__)


@books_bp.route("/api/v1/books", methods=["GET"])
@api_token_required
def get_books():
    """Get all books for the current user."""
    current_app.logger.debug("Entered get_books route")

    try:
        books_list = BookService.get_user_books(g.current_user.id)
        return jsonify([book.to_dict() for book in books_list])
    except Exception as e:
        current_app.logger.error(f"Error getting books: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@books_bp.route("/api/v1/books", methods=["POST"])
@api_token_required
def create_book():
    """Create a new book."""
    current_app.logger.debug("Entered create_book route")

    try:
        data = request.get_json()

        # Validate input using schema
        schema = CreateBookSchema()
        validated_data = schema.load(data)

        # Use service layer
        book = BookService.create_book(
            user_id=g.current_user.id, name=validated_data["name"]
        )

        return (
            jsonify({"message": "Book created successfully", "book": book.to_dict()}),
            201,
        )

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating book: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@books_bp.route("/api/v1/books/<int:book_id>", methods=["GET"])
@api_token_required
def get_book(book_id):
    """Get a specific book."""
    current_app.logger.debug(f"Entered get_book route for ID: {book_id}")

    try:
        book = BookService.get_book_by_id(book_id, g.current_user.id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        return jsonify(book.to_dict())
    except BookNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting book {book_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@books_bp.route("/api/v1/books/<int:book_id>", methods=["PUT"])
@api_token_required
def update_book(book_id):
    """Update a book."""
    current_app.logger.debug(f"Entered update_book route for ID: {book_id}")

    try:
        data = request.get_json()

        # Validate input using schema
        schema = UpdateBookSchema()
        validated_data = schema.load(data)

        # Use service layer
        book = BookService.update_book(
            book_id=book_id, user_id=g.current_user.id, name=validated_data["name"]
        )

        return jsonify({"message": "Book updated successfully", "book": book.to_dict()})

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except BookNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating book {book_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@books_bp.route("/api/v1/books/<int:book_id>/set-active", methods=["POST"])
@api_token_required
def set_active_book(book_id):
    """Set a book as active for the current user."""
    current_app.logger.debug(f"Entered set_active_book route for ID: {book_id}")

    try:
        book = BookService.set_active_book(book_id, g.current_user.id)

        return jsonify(
            {
                "message": f"Book '{book.name}' set as active",
                "active_book": book.to_dict(),
            }
        )

    except BookNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error setting active book {book_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@books_bp.route("/api/v1/books/active", methods=["GET"])
@api_token_required
def get_active_book():
    """Get the current user's active book."""
    current_app.logger.debug("Entered get_active_book route")

    try:
        active_book = BookService.get_active_book(g.current_user.id)

        if not active_book:
            return jsonify({})  # Active book is not set or not found

        return jsonify(active_book.to_dict())

    except Exception as e:
        current_app.logger.error(f"Error getting active book: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@books_bp.route("/api/v1/books/<int:book_id>", methods=["DELETE"])
@api_token_required
def delete_book(book_id):
    """Delete a book and all its associated accounts and transactions."""
    current_app.logger.debug(f"Entered delete_book route for ID: {book_id}")

    try:
        BookService.delete_book(book_id, g.current_user.id)

        return jsonify(
            {"message": "Book and all associated accounts deleted successfully"}
        )

    except BookNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error deleting book {book_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
