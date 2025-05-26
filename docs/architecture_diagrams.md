# Kanakku Architecture Diagrams

This document contains architectural diagrams for the Kanakku application using Mermaid notation.

## 1. High-Level System Architecture

```mermaid
flowchart TD
    User[User] --> |uses| Frontend
    Developer[Developer] --> |monitors via| AdminServer
    Frontend[React Frontend] --> |HTTP/REST API| Backend
    Backend[Flask Backend] --> |SQL/ORM| Database[(Database)]
    Backend --> |optional| Ledger[Ledger CLI]
    AdminServer[Admin MCP Server] --> |SSH| ProductionServer[Production Server]
    
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
    
    subgraph "Admin & Monitoring"
        AdminServer
        CursorIDE[Cursor IDE]
        AdminServer --> |MCP Protocol| CursorIDE
    end
    
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px;
    classDef backend fill:#4a4a4a,stroke:#333,stroke-width:2px,color:white;
    classDef database fill:#f5b042,stroke:#333,stroke-width:2px;
    classDef external fill:#9c9c9c,stroke:#333,stroke-width:2px;
    classDef user fill:#b8e986,stroke:#333,stroke-width:2px;
    classDef admin fill:#e74c3c,stroke:#333,stroke-width:2px,color:white;
    
    class Frontend,FrontComponents,FrontAPI,FrontRouter,FrontState frontend;
    class Backend,BackAPI,BackAuth,BackModels,BackServices backend;
    class Database database;
    class Ledger external;
    class User user;
    class AdminServer,CursorIDE,ProductionServer,Developer admin;
```

## 2. Backend Component Architecture

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
        
        Models[Models\nmodels.py]
        Database[(Database)] <--> |SQLAlchemy| Models
    end
    
    AuthAPI & AccountsAPI & TransactionsAPI & BooksAPI & ReportsAPI & LedgerAPI & GeneralAPI & PreambleAPI --> Models
    
    classDef client fill:#b8e986,stroke:#333,stroke-width:2px;
    classDef core fill:#4a4a4a,stroke:#333,stroke-width:2px,color:white;
    classDef blueprint fill:#3498db,stroke:#333,stroke-width:2px,color:white;
    classDef database fill:#f5b042,stroke:#333,stroke-width:2px;
    
    class Client client;
    class ApplicationFactory,Config,Extensions,ErrorHandlers,Models core;
    class AuthAPI,AccountsAPI,TransactionsAPI,BooksAPI,ReportsAPI,LedgerAPI,GeneralAPI,PreambleAPI,Blueprints blueprint;
    class Database database;
```

## 3. Frontend Component Architecture

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

## 4. Database Entity Relationship Diagram (ERD)

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

## 5. Authentication Flow

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

## 6. Transaction Creation Flow

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

## 7. API Request Flow

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

## 8. Deployment Architecture

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

## 9. Admin Server (MCP Server) Architecture

```mermaid
flowchart TD
    CursorIDE[Cursor IDE] --> |MCP Protocol| AdminServer[Admin MCP Server]
    AdminServer --> |SSH Connection| ProductionServer[Production Server]
    
    subgraph "Admin Server Components"
        MCPServer[MCP Server Implementation]
        SSHClient[SSH Client]
        LogReader[Log Reader]
        CommandExecutor[Safe Command Executor]
        ServiceMonitor[Service Monitor]
    end
    
    subgraph "Production Server Resources"
        AppLogs[Application Logs]
        SystemLogs[System Logs]
        NginxLogs[Nginx Logs]
        Services[System Services]
        SystemMetrics[System Metrics]
    end
    
    AdminServer --> MCPServer
    MCPServer --> SSHClient
    MCPServer --> LogReader
    MCPServer --> CommandExecutor
    MCPServer --> ServiceMonitor
    
    SSHClient --> AppLogs
    SSHClient --> SystemLogs
    SSHClient --> NginxLogs
    SSHClient --> Services
    SSHClient --> SystemMetrics
    
    classDef ide fill:#61dafb,stroke:#333,stroke-width:2px;
    classDef admin fill:#e74c3c,stroke:#333,stroke-width:2px,color:white;
    classDef server fill:#4a4a4a,stroke:#333,stroke-width:2px,color:white;
    classDef resources fill:#f5b042,stroke:#333,stroke-width:2px;
    
    class CursorIDE ide;
    class AdminServer,MCPServer,SSHClient,LogReader,CommandExecutor,ServiceMonitor admin;
    class ProductionServer server;
    class AppLogs,SystemLogs,NginxLogs,Services,SystemMetrics resources;
```

## 10. Admin Server Usage Flow

```mermaid
sequenceDiagram
    participant Developer
    participant CursorIDE as Cursor IDE
    participant AdminServer as Admin MCP Server
    participant ProductionServer as Production Server
    
    Developer->>CursorIDE: "Show me application logs"
    CursorIDE->>AdminServer: MCP Tool Call: read_log
    AdminServer->>ProductionServer: SSH: tail -n 100 /opt/kanakku/logs/kanakku.log
    ProductionServer-->>AdminServer: Log Content
    AdminServer-->>CursorIDE: Formatted Log Response
    CursorIDE-->>Developer: Display Logs
    
    Developer->>CursorIDE: "Search for errors in last hour"
    CursorIDE->>AdminServer: MCP Tool Call: search_logs
    AdminServer->>ProductionServer: SSH: grep "error" logs --since "1 hour ago"
    ProductionServer-->>AdminServer: Search Results
    AdminServer-->>CursorIDE: Formatted Search Results
    CursorIDE-->>Developer: Display Error Matches
    
    Developer->>CursorIDE: "Check service status"
    CursorIDE->>AdminServer: MCP Tool Call: service_status
    AdminServer->>ProductionServer: SSH: systemctl status kanakku
    ProductionServer-->>AdminServer: Service Status
    AdminServer-->>CursorIDE: Formatted Status Response
    CursorIDE-->>Developer: Display Service Health
``` 