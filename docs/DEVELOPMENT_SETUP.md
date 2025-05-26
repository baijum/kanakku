# Development Setup Guide

This guide provides detailed instructions for setting up the Kanakku development environment using the new unified monorepo structure.

## Quick Start

For experienced developers who want to get started quickly:

```bash
git clone https://github.com/yourusername/kanakku.git
cd kanakku
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cd backend && ./run-backend.sh
```

## Detailed Setup

### 1. Prerequisites

Ensure you have the following installed:

- **Python 3.12+**: Required for all backend components
- **Node.js 18+**: Required for frontend development
- **PostgreSQL**: Database server
- **Redis**: Required for background job processing
- **Git**: Version control

#### Installing Prerequisites

**macOS (using Homebrew):**
```bash
brew install python@3.12 node postgresql redis git
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv nodejs npm postgresql redis-server git
```

**Windows:**
- Install Python 3.12+ from [python.org](https://python.org)
- Install Node.js from [nodejs.org](https://nodejs.org)
- Install PostgreSQL from [postgresql.org](https://postgresql.org)
- Install Redis from [redis.io](https://redis.io)

### 2. Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/yourusername/kanakku.git
cd kanakku

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies (backend, banktransactions, dev tools)
pip install -e ".[dev]"
```

### 3. Database Setup

#### PostgreSQL Setup

1. **Start PostgreSQL service:**
   ```bash
   # macOS (Homebrew)
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo systemctl start postgresql
   
   # Windows
   # Start PostgreSQL service from Services panel
   ```

2. **Create database and user:**
   ```bash
   # Connect to PostgreSQL
   psql postgres
   
   # Create database and user
   CREATE DATABASE kanakku;
   CREATE USER kanakku_user WITH PASSWORD 'kanakku_password';
   GRANT ALL PRIVILEGES ON DATABASE kanakku TO kanakku_user;
   \q
   ```

3. **Configure environment variables:**
   ```bash
   # Create .env file in project root
   cat > .env << EOF
   DATABASE_URL=postgresql://kanakku_user:kanakku_password@localhost:5432/kanakku
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   EOF
   ```

#### Redis Setup

1. **Start Redis service:**
   ```bash
   # macOS (Homebrew)
   brew services start redis
   
   # Ubuntu/Debian
   sudo systemctl start redis-server
   
   # Windows
   # Download and run Redis from GitHub releases
   ```

2. **Add Redis URL to .env:**
   ```bash
   echo "REDIS_URL=redis://localhost:6379/0" >> .env
   ```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`.

### 5. Backend Setup

```bash
cd backend

# Run database migrations
flask db upgrade

# Start the backend server
./run-backend.sh
```

The backend will be available at `http://localhost:8000`.

### 6. Email Automation Setup (Optional)

For bank transaction processing via email:

1. **Add Google API key to .env:**
   ```bash
   echo "GOOGLE_API_KEY=your-gemini-api-key" >> .env
   echo "ENCRYPTION_KEY=your-32-byte-base64-key" >> .env
   ```

2. **Start email workers:**
   ```bash
   cd banktransactions/email_automation
   
   # Start worker (in one terminal)
   python run_worker.py
   
   # Start scheduler (in another terminal)
   python run_scheduler.py --interval 300
   ```

## Development Workflow

### Running Tests

```bash
# Run all Python tests
python -m pytest backend/tests/ banktransactions/tests/ -v

# Run with coverage
python -m pytest backend/tests/ banktransactions/tests/ --cov=backend --cov=banktransactions

# Run specific test file
python -m pytest backend/tests/test_auth.py -v

# Use convenience script
./test.sh
```

### Code Quality

```bash
# Run linting
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Format code
black .

# Type checking
mypy backend/ banktransactions/

# Use convenience script
./lint.sh
```

### Adding Dependencies

To add new Python dependencies:

1. **Edit `pyproject.toml`:**
   ```toml
   dependencies = [
       # ... existing dependencies
       "new-package==1.0.0",
   ]
   ```

2. **Reinstall in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

### Database Migrations

```bash
cd backend

# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Downgrade (if needed)
flask db downgrade
```

## Troubleshooting

### Common Issues

1. **Import errors after installation:**
   ```bash
   # Ensure you're in the project root and virtual environment is active
   pip install -e ".[dev]"
   ```

2. **Database connection errors:**
   ```bash
   # Check PostgreSQL is running
   pg_isready
   
   # Check database exists
   psql -d kanakku -c "SELECT 1;"
   ```

3. **Redis connection errors:**
   ```bash
   # Check Redis is running
   redis-cli ping
   ```

4. **Port conflicts:**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Kill process if needed
   kill -9 <PID>
   ```

### Getting Help

- Check the [FAQ](faq.md) for common questions
- Review [Architecture Documentation](ARCHITECTURE.md) for system understanding
- Check [Redis Queue Debugging](redis-queue-debugging.md) for background job issues
- Create an issue on GitHub for bugs or feature requests

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- Black Formatter
- Ruff
- ES7+ React/Redux/React-Native snippets

### PyCharm

1. Open the project root directory
2. Configure Python interpreter to use the virtual environment
3. Enable Django support (for Flask compatibility)
4. Configure code style to use Black

## Production Considerations

For production deployment:

- See [Production Deployment Guide](PRODUCTION_DEPLOYMENT.md)
- Review [Production Checklist](PRODUCTION_CHECKLIST.md)
- Use environment-specific configuration
- Set up proper logging and monitoring

## Next Steps

After setup:

1. Read the [User Manual](user_manual.md) to understand features
2. Review [API Documentation](api_documentation.md) for backend development
3. Check [Architecture Diagrams](architecture_diagrams.md) for system overview
4. Explore the codebase starting with `backend/app/` and `frontend/src/` 