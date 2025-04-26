# Kanakku - Architecture Documentation

## Overview

Kanakku is a full-stack expense tracking application built with a Flask backend and React frontend. The application provides users with a way to manage financial transactions using double-entry bookkeeping principles inspired by the Ledger CLI tool.

## System Architecture

### High-Level Architecture

```
+------------------+         +------------------+         +-------------+
|                  |  HTTP   |                  |  SQL    |             |
|  React Frontend  <-------->+  Flask Backend   <-------->+  Database   |
|  (frontend/)     |  REST   |  (backend/)      |         |  (SQLite)   |
|                  |  API    |                  |         |             |
+------------------+         +------------------+         +-------------+
                                     |
                                     | Execute commands
                                     v
                              +-------------+
                              |             |
                              | Ledger CLI  |
                              | (optional)  |
                              |             |
                              +-------------+
```

### Backend Architecture (Flask)

The backend follows a modular architecture using Flask Blueprints to organize the code by functionality:

1. **Application Factory Pattern** (`backend/app/__init__.py`):
   - Creates and configures the Flask application
   - Registers all blueprints and extensions
   - Sets up error handlers and middleware

2. **Models** (`backend/app/models.py`):
   - SQLAlchemy models representing the database schema
   - Key models include User, Book, Account, Transaction, Preamble, and ApiToken

3. **API Blueprints**:
   - `auth.py`: Authentication routes (login, register, JWT tokens)
   - `accounts.py`: Account management (CRUD operations)
   - `transactions.py`: Transaction management (CRUD operations)
   - `books.py`: Book entries for advanced accounting
   - `ledger.py`: Ledger CLI integration
   - `reports.py`: Financial reporting functionality
   - `api.py`: General API endpoints (health check, etc.)

4. **Configuration** (`backend/app/config.py`):
   - Environment-based configuration
   - Secret keys, database URLs, and other settings

5. **Extensions** (`backend/app/extensions.py`):
   - Flask extensions configuration (SQLAlchemy, JWT, CORS, etc.)

6. **Error Handling** (`backend/app/errors.py`):
   - Custom exception classes
   - Error handlers for different HTTP status codes

### Frontend Architecture (React)

The frontend is built with React and follows a component-based architecture:

1. **Application Entry** (`frontend/src/App.js`):
   - Main application component
   - Routing using React Router
   - Authentication state management

2. **Components**:
   - Organized by functionality in `frontend/src/components/`
   - Key components include:
     - Authentication components (login, register)
     - Transaction management (add, view, edit)
     - Account management
     - Book management
     - Dashboard for overview

3. **API Integration** (`frontend/src/api/`):
   - Axios-based API client
   - API endpoint wrappers for different resources

4. **UI Framework**:
   - Material-UI (MUI) for component styling and layout

## Database Schema

```
+---------------+       +---------------+       +---------------+
|     User      |       |     Book      |       |    Account    |
+---------------+       +---------------+       +---------------+
| id            |<---+  | id            |<---+  | id            |
| email         |    |  | user_id       +--+ |  | user_id       |
| password_hash |    |  | name          |  | |  | book_id       |
| name          |    |  | created_at    |  | +--+ name          |
| active_book_id+----+  | updated_at    |  |    | description   |
| is_active     |       +---------------+  |    | currency      |
| is_admin      |                          |    | balance       |
| created_at    |       +---------------+  |    | created_at    |
| updated_at    |       | Transaction   |  |    +---------------+
| reset_token   |       +---------------+  |
| google_id     |<---+  | id            |  |
| picture       |    |  | user_id       +--+
+---------------+    |  | book_id       +--+
                     |  | account_id    |
+---------------+    |  | date          |
|   Preamble    |    |  | description   |
+---------------+    |  | payee         |
| id            |    |  | amount        |
| user_id       +----+  | currency      |
| name          |       | status        |
| content       |       | created_at    |
| is_default    |       +---------------+
| created_at    |
| updated_at    |
+---------------+
```

## Authentication Flow

1. **Traditional Authentication**:
   - User registers with email and password
   - User logs in to receive JWT token
   - JWT token is included in subsequent API requests

2. **Google OAuth Integration**:
   - User initiates Google login
   - Backend handles OAuth flow with Google
   - User account is created/linked with Google ID
   - JWT token is issued for authenticated session

## Key Technologies

### Backend
- Flask: Web framework
- SQLAlchemy: ORM for database operations
- Flask-JWT-Extended: JWT authentication
- Flask-CORS: Cross-origin resource sharing

### Frontend
- React: UI library
- Material-UI: Component library
- Axios: HTTP client
- React Router: Client-side routing

### Development & Deployment
- Docker: Containerization
- Nginx: Reverse proxy for production
- Systemd: Service management for production deployment

## Security Considerations

1. **Authentication**:
   - JWT tokens with proper expiration
   - Password hashing with Werkzeug
   - Token-based password reset

2. **Authorization**:
   - Role-based access control (admin vs. regular users)
   - Resource ownership validation

3. **Input Validation**:
   - Comprehensive validation on both frontend and backend
   - SQLAlchemy ORM to prevent SQL injection

4. **API Security**:
   - CORS configuration
   - Rate limiting (TODO)
   - API tokens for programmatic access

## Future Architectural Improvements

1. **Caching Layer**:
   - Implement Redis for caching frequently accessed data
   - Cache expensive report calculations

2. **Microservices**:
   - Split monolithic backend into microservices
   - Separate authentication, transaction processing, and reporting

3. **Real-time Updates**:
   - Implement WebSockets for real-time transaction updates
   - Push notifications for important events

4. **Scalability**:
   - Move from SQLite to PostgreSQL for production
   - Implement horizontal scaling with load balancing 