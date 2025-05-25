# Kanakku - Architecture Documentation

## Overview

Kanakku is a full-stack expense tracking application built with a Flask backend and React frontend. The application provides users with a way to manage financial transactions using double-entry bookkeeping principles inspired by the Ledger CLI tool.

## System Architecture

### High-Level Architecture

```mermaid
flowchart TD
    User[User] --> |uses| Frontend
    Frontend[React Frontend] --> |HTTP/REST API| Backend
    Backend[Flask Backend] --> |SQL/ORM| Database[(Database)]
    Backend --> |optional| Ledger[Ledger CLI]
    
    subgraph "Frontend (React)"
        FrontComponents[Components]
        FrontAPI[API Client]
        FrontRouter[Router]
        FrontState[State Management]
    end
    
    subgraph "Backend (Flask)"
        BackAPI[API Endpoints]
        BackAuth[Authentication]
        BackModels[Data Models]
        BackServices[Business Logic]
    end
    
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px;
    classDef backend fill:#4a4a4a,stroke:#333,stroke-width:2px,color:white;
    classDef database fill:#f5b042,stroke:#333,stroke-width:2px;
    classDef external fill:#9c9c9c,stroke:#333,stroke-width:2px;
    classDef user fill:#b8e986,stroke:#333,stroke-width:2px;
    
    class Frontend,FrontComponents,FrontAPI,FrontRouter,FrontState frontend;
    class Backend,BackAPI,BackAuth,BackModels,BackServices backend;
    class Database database;
    class Ledger external;
    class User user;
```

### Backend Architecture (Flask)

The backend follows a modular architecture using Flask Blueprints to organize the code by functionality:

```mermaid
flowchart LR
    Client[Client] --> |HTTP Request| ApplicationFactory
    
    subgraph "Flask Application"
        ApplicationFactory[Application Factory\n__init__.py] --> Config[Configuration\nconfig.py]
        ApplicationFactory --> Extensions[Extensions\nextensions.py]
        ApplicationFactory --> ErrorHandlers[Error Handlers\nerrors.py]
        ApplicationFactory --> Blueprints[Blueprints]
        
        Blueprints --> AuthAPI[auth.py\nAuthentication]
        Blueprints --> AccountsAPI[accounts.py\nAccount Management]
        Blueprints --> TransactionsAPI[transactions.py\nTransaction Management]
        Blueprints --> BooksAPI[books.py\nBook Management]
        Blueprints --> ReportsAPI[reports.py\nFinancial Reports]
        Blueprints --> LedgerAPI[ledger.py\nLedger Integration]
        Blueprints --> GeneralAPI[api.py\nGeneral Endpoints]
        Blueprints --> PreambleAPI[preamble.py\nPreamble Templates]
        Blueprints --> SwaggerAPI[swagger.py\nSwagger Documentation]
        
        Models[Models\nmodels.py]
        Database[(Database)] <--> |SQLAlchemy| Models
    end
    
    AuthAPI & AccountsAPI & TransactionsAPI & BooksAPI & ReportsAPI & LedgerAPI & GeneralAPI & PreambleAPI & SwaggerAPI --> Models
    
    classDef client fill:#b8e986,stroke:#333,stroke-width:2px;
    classDef core fill:#4a4a4a,stroke:#333,stroke-width:2px,color:white;
    classDef blueprint fill:#3498db,stroke:#333,stroke-width:2px,color:white;
    classDef database fill:#f5b042,stroke:#333,stroke-width:2px;
    
    class Client client;
    class ApplicationFactory,Config,Extensions,ErrorHandlers,Models core;
    class AuthAPI,AccountsAPI,TransactionsAPI,BooksAPI,ReportsAPI,LedgerAPI,GeneralAPI,PreambleAPI,SwaggerAPI blueprint;
    class Database database;
```

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
   - `preamble.py`: Preamble template management
   - `swagger.py`: Swagger API documentation

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

```mermaid
flowchart TD
    AppEntry[App.js\nMain Entry Point] --> Router[React Router]
    Router --> Routes
    
    subgraph "Routes"
        Login[Login Page]
        Register[Register Page]
        Dashboard[Dashboard]
        Accounts[Accounts Management]
        Transactions[Transactions Management]
        Books[Books Management]
        Reports[Financial Reports]
    end
    
    subgraph "Components"
        AuthComponents[Authentication Components]
        UIComponents[UI Components]
        FormComponents[Form Components]
        TableComponents[Table Components]
        ChartComponents[Chart Components]
    end
    
    subgraph "API Integration"
        APIClient[API Client\naxiosInstance]
        AuthAPI[Auth API]
        AccountsAPI[Accounts API]
        TransactionsAPI[Transactions API]
        BooksAPI[Books API]
        ReportsAPI[Reports API]
    end
    
    Routes --> Components
    Components --> APIIntegration
    
    classDef entry fill:#61dafb,stroke:#333,stroke-width:2px;
    classDef route fill:#3498db,stroke:#333,stroke-width:2px;
    classDef component fill:#9c9c9c,stroke:#333,stroke-width:2px;
    classDef api fill:#f5b042,stroke:#333,stroke-width:2px;
    
    class AppEntry,Router entry;
    class Login,Register,Dashboard,Accounts,Transactions,Books,Reports route;
    class AuthComponents,UIComponents,FormComponents,TableComponents,ChartComponents component;
    class APIClient,AuthAPI,AccountsAPI,TransactionsAPI,BooksAPI,ReportsAPI api;
```

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
   - Axios-based API client with interceptors for authentication and CSRF
   - API endpoint wrappers for different resources

4. **UI Framework**:
   - Material-UI (MUI) for component styling and layout

## Database Schema

```mermaid
erDiagram
    User ||--o{ Book : "creates"
    User ||--o{ Transaction : "owns"
    User ||--o{ Account : "owns"
    User ||--o{ Preamble : "creates"
    User ||--o{ ApiToken : "owns"
    User ||--|| Book : "has active"
    Book ||--o{ Account : "contains"
    Book ||--o{ Transaction : "contains"
    Account ||--o{ Transaction : "has"
    
    User {
        int id PK
        string email
        string password_hash
        string name
        int active_book_id FK
        boolean is_active
        boolean is_admin
        datetime created_at
        datetime updated_at
        string reset_token
        datetime reset_token_expires_at
        string google_id
        string picture
    }
    
    Book {
        int id PK
        int user_id FK
        string name
        datetime created_at
        datetime updated_at
    }
    
    Account {
        int id PK
        int user_id FK
        int book_id FK
        string name
        string description
        string currency
        float balance
        datetime created_at
    }
    
    Transaction {
        int id PK
        int user_id FK
        int book_id FK
        int account_id FK
        date date
        string description
        string payee
        float amount
        string currency
        string status
        datetime created_at
    }
    
    Preamble {
        int id PK
        int user_id FK
        string name
        text content
        boolean is_default
        datetime created_at
        datetime updated_at
    }
    
    ApiToken {
        int id PK
        int user_id FK
        string token
        string name
        datetime expires_at
        boolean is_active
        datetime created_at
        datetime last_used_at
    }
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Google
    participant Database
    
    %% Traditional Authentication Flow
    User->>Frontend: Enter Credentials
    Frontend->>Backend: POST /api/v1/auth/login
    Backend->>Database: Verify Credentials
    Database-->>Backend: Authentication Result
    
    alt Authentication Success
        Backend-->>Frontend: Return JWT Token
        Frontend->>Frontend: Store Token in localStorage
        Frontend-->>User: Redirect to Dashboard
    else Authentication Failure
        Backend-->>Frontend: Return Error
        Frontend-->>User: Display Error Message
    end
    
    %% Google OAuth Authentication Flow
    User->>Frontend: Click "Sign in with Google"
    Frontend->>Backend: GET /api/v1/auth/google
    Backend->>Google: Initialize OAuth Flow
    Google-->>User: Display Consent Screen
    User->>Google: Grant Permissions
    Google-->>Backend: Send OAuth Callback with Code
    Backend->>Google: Exchange Code for Token
    Google-->>Backend: Return Access Token
    Backend->>Backend: Create/Update User with Google ID
    Backend-->>Frontend: Return JWT Token
    Frontend->>Frontend: Store Token in localStorage
    Frontend-->>User: Redirect to Dashboard
```

1. **Traditional Authentication**:
   - User registers with email and password
   - User logs in to receive JWT token
   - JWT token is included in subsequent API requests

2. **Google OAuth Integration**:
   - User initiates Google login
   - Backend handles OAuth flow with Google
   - User account is created/linked with Google ID
   - JWT token is issued for authenticated session

## API Request Flow

```mermaid
flowchart TD
    subgraph "Frontend"
        React[React Component] --> |1. Makes API Request| Axios
        Axios[Axios Client] --> |2. Sends HTTP Request with JWT| Flask
    end
    
    subgraph "Backend"
        Flask[Flask Application] --> |3. JWT Authentication| JWTMiddleware[JWT Middleware]
        JWTMiddleware --> |4. Route to Endpoint| APIBlueprint[API Blueprint]
        APIBlueprint --> |5. Process Request| BusinessLogic[Business Logic]
        BusinessLogic --> |6. Database Operations| SQLAlchemy
        SQLAlchemy --> |7. Execute SQL| Database[(Database)]
        BusinessLogic --> |8. Return Response| APIBlueprint
        APIBlueprint --> |9. Format Response| Flask
    end
    
    Flask --> |10. HTTP Response| Axios
    Axios --> |11. Process Response| React
    
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px;
    classDef backend fill:#4a4a4a,stroke:#333,stroke-width:2px,color:white;
    classDef database fill:#f5b042,stroke:#333,stroke-width:2px;
    
    class React,Axios frontend;
    class Flask,JWTMiddleware,APIBlueprint,BusinessLogic,SQLAlchemy backend;
    class Database database;
```

## Transaction Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database
    
    User->>Frontend: Fill Transaction Form
    Frontend->>Frontend: Validate Form Data
    
    alt Validation Success
        Frontend->>Backend: POST /api/v1/transactions
        Backend->>Backend: Validate Request Data
        Backend->>Database: Create Transaction
        Database-->>Backend: Return Created Transaction
        Backend->>Backend: Update Account Balance
        Backend-->>Frontend: Return Success Response
        Frontend-->>User: Display Success Message
    else Validation Failure
        Frontend-->>User: Display Validation Errors
    end
```

## Deployment Architecture

```mermaid
flowchart TD
    User[User] --> |HTTPS| Nginx
    
    subgraph "Production Server"
        Nginx[Nginx Reverse Proxy] --> |Proxy Pass /api| Gunicorn
        Nginx --> |Serve Static Files| StaticFiles[Static Files]
        Gunicorn[Gunicorn WSGI Server] --> Flask[Flask Application]
        Flask --> PostgreSQL[(PostgreSQL Database)]
        SystemD[SystemD Service] --> |Manages| Gunicorn
    end
    
    subgraph "Development Environment"
        FlaskDev[Flask Development Server]
        ReactDev[React Development Server]
        SQLiteDev[(SQLite Database)]
        FlaskDev --> SQLiteDev
    end
    
    classDef user fill:#b8e986,stroke:#333,stroke-width:2px;
    classDef server fill:#4a4a4a,stroke:#333,stroke-width:2px,color:white;
    classDef proxy fill:#3498db,stroke:#333,stroke-width:2px,color:white;
    classDef app fill:#9c9c9c,stroke:#333,stroke-width:2px;
    classDef database fill:#f5b042,stroke:#333,stroke-width:2px;
    classDef development fill:#e74c3c,stroke:#333,stroke-width:2px,color:white;
    
    class User user;
    class Nginx proxy;
    class Gunicorn,SystemD server;
    class Flask,StaticFiles app;
    class PostgreSQL,SQLiteDev database;
    class FlaskDev,ReactDev development;
```

## Key Technologies

### Backend

- Flask: Web framework
- SQLAlchemy: ORM for database operations
- Flask-JWT-Extended: JWT authentication
- Flask-CORS: Cross-origin resource sharing
- Swagger: API documentation

### Frontend

- React: UI library
- Material-UI: Component library
- Axios: HTTP client with interceptors for authentication
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
   - Google OAuth integration

2. **Authorization**:
   - Role-based access control (admin vs. regular users)
   - Resource ownership validation
   - API token-based access for programmatic usage

3. **Input Validation**:
   - Comprehensive validation on both frontend and backend
   - SQLAlchemy ORM to prevent SQL injection

4. **API Security**:
   - CORS configuration
   - CSRF protection for non-GET requests
   - Rate limiting for authentication endpoints
   - Secure cookie handling
   - Bearer token authentication

5. **Error Handling**:
   - Custom error handlers with appropriate HTTP status codes
   - Sanitized error messages in production

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

5. **API Documentation**:
   - Enhanced Swagger documentation
   - Interactive API explorer

## Bank Transaction Processing System

The bank transaction processing system is a separate module that automates the extraction and categorization of transactions from bank emails.

### System Architecture

```mermaid
flowchart TD
    EmailServer[Email Server] --> |IMAP| EmailFetcher[Email Fetcher]
    EmailFetcher --> |Raw Emails| EmailParser[Email Parser]
    EmailParser --> |Transaction Data| TransactionProcessor[Transaction Processor]
    TransactionProcessor --> |API Calls| Backend[Backend API]
    
    subgraph "Email Processing"
        EmailFetcher
        EmailParser
        TransactionProcessor
    end
    
    subgraph "Configuration"
        Database[Database Mappings]
        EnvVars[Environment Variables]
    end
    
    Database --> EmailParser
    Database --> TransactionProcessor
    EnvVars --> EmailFetcher
    
    classDef email fill:#61dafb,stroke:#333,stroke-width:2px;
    classDef processor fill:#4a4a4a,stroke:#333,stroke-width:2px,color:white;
    classDef config fill:#f5b042,stroke:#333,stroke-width:2px;
    classDef backend fill:#9c9c9c,stroke:#333,stroke-width:2px;
    
    class EmailServer,EmailFetcher,EmailParser email;
    class TransactionProcessor processor;
    class Database,EnvVars config;
    class Backend backend;
```

### Components

1. **Email Fetcher** (`banktransactions/imap_client.py`):
   - Connects to email servers via IMAP
   - Fetches new transaction emails
   - Handles email deduplication
   - Manages email server connections

2. **Email Parser** (`banktransactions/email_parser.py`):
   - Extracts transaction details from email bodies
   - Handles different bank email formats
   - Parses transaction amounts, dates, and descriptions
   - Extracts masked account numbers

3. **Transaction Processor** (`banktransactions/main.py`):
   - Processes extracted transaction data
   - Maps transactions to expense categories
   - Maps bank accounts to ledger accounts
   - Submits transactions to the backend API

4. **Configuration** (Database-stored mappings):
   - Bank account mapping
   - Expense category mapping
   - Transaction descriptions
   - Environment variables for credentials

### Data Flow

1. **Email Fetching**:
   - System connects to email server using IMAP
   - Fetches new transaction emails
   - Checks for duplicates using processed IDs

2. **Transaction Extraction**:
   - Parses email body for transaction details
   - Extracts amount, date, description
   - Identifies bank account from masked number

3. **Transaction Processing**:
   - Maps bank account to ledger account
   - Categorizes transaction based on merchant
   - Generates transaction description
   - Creates transaction data structure

4. **API Integration**:
   - Submits transaction to backend API
   - Handles API errors and retries
   - Updates processed email IDs

### Configuration

The system uses two types of configuration:

1. **Environment Variables**:

   ```bash
   GMAIL_USERNAME=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   BANK_EMAILS=alerts@axisbank.com,alerts@icicibank.com
   ```

2. **Database-stored Mappings** (accessed via API):
   - Bank account mappings: Map masked account numbers to ledger accounts
   - Expense account mappings: Map merchant names to expense categories and descriptions
   - Managed through the web interface or API endpoints

### Error Handling

The system includes robust error handling for:

- Email server connection issues
- Email parsing errors
- Transaction mapping failures
- API communication errors
- Configuration problems

### Integration with Main Application

The bank transaction processing system integrates with the main application through:

- REST API endpoints for transaction submission
- Database-stored configuration for account mapping
- Common transaction data model
- Unified error handling 