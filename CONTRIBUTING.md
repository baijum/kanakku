# Contributing to Kanakku

Thank you for your interest in contributing to Kanakku! This document provides guidelines and rules for contributing to the project.

## Code Style and Standards

### Python (Backend)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for function parameters and return values
- Keep functions small and focused (ideally under 20 lines)
- Use meaningful variable and function names
- Add docstrings for all public functions and classes
- Use snake_case for variables and functions
- Use PascalCase for class names
- Default currency should be INR with proper symbol formatting

Example:

```python
def process_transaction(transaction_data: dict) -> dict:
    """
    Process a transaction and return the formatted result.
    
    Args:
        transaction_data (dict): The transaction data to process
        
    Returns:
        dict: The processed transaction data
    """
    # Implementation
```

### JavaScript/React (Frontend)

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks
- Keep components small and focused
- Use meaningful prop and variable names
- Use camelCase for variables and functions
- Use PascalCase for component names
- Use TypeScript for new components (if possible)
- Use Material-UI (MUI) for UI components
- Default currency should be displayed as ₹ (INR)

Example:

```jsx
const TransactionForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({});
  
  const handleSubmit = useCallback((event) => {
    event.preventDefault();
    onSubmit(formData);
  }, [formData, onSubmit]);
  
  return (
    // JSX
  );
};
```

## API Documentation

When adding or modifying API endpoints:

1. Update the `backend/swagger.yaml` file with your changes
2. Include:
   - Endpoint path and method
   - Request parameters and body schema
   - Response schema
   - Authentication requirements
   - Example requests and responses

## Git Workflow

1. Create a new branch for each feature/fix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:

   ```bash
   git commit -m "feat: add new transaction form"
   ```

3. Push your branch:

   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request

### Commit Message Format

- Use [Conventional Commits](https://www.conventionalcommits.org/) format
- Types: feat, fix, docs, style, refactor, test, chore
- Example: `feat: add transaction form validation`

## Testing

### Backend

- Write unit tests for all new functions
- Use pytest for testing
- Aim for at least 80% test coverage
- Include tests for error cases
- Run tests with:

  ```bash
  cd backend
  python -m pytest -v tests/
  ```

### Frontend

- Write tests for all new components
- Use React Testing Library
- Test component behavior, not implementation
- Include tests for user interactions
- Run tests with:

  ```bash
  cd frontend
  npm test
  ```

## Documentation

- Update README.md for significant changes
- Document new features in the code
- Keep comments up to date
- Use JSDoc for JavaScript functions
- Use Python docstrings for Python functions
- Document bug fixes in the `fixes/` directory for major issues

## Security

- Never commit sensitive information (API keys, passwords)
- Validate all user input
- Use environment variables for configuration
- Follow security best practices for both frontend and backend
- Use JWT tokens properly (store identity as a string)

## Performance

- Optimize database queries
- Minimize API calls
- Use proper indexing
- Implement caching where appropriate
- Optimize React renders with useMemo and useCallback

## Error Handling

- Use proper error handling in both frontend and backend
- Provide meaningful error messages
- Log errors appropriately
- Handle edge cases gracefully

## Code Review Process

1. Create a Pull Request
2. Request review from at least one maintainer
3. Address all review comments
4. Ensure all tests pass
5. Get approval before merging

## Getting Started

1. Fork the repository
2. Clone your fork
3. Set up the unified development environment:

   ```bash
   # Unified setup (recommended)
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   
   # Frontend
   cd frontend
   npm install
   ```

4. Make your changes
5. Run tests:

   ```bash
   # All Python tests (backend + banktransactions)
   python -m pytest backend/tests/ banktransactions/tests/ -v
   
   # Or use convenience script
   ./test.sh
   
   # Frontend
   cd frontend
   npm test
   ```

### Alternative Setup (Legacy)

If you prefer individual module setup:

```bash
# Backend only
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Bank transactions only
cd banktransactions
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. Submit a Pull Request

## Running the Application

### Backend

```bash
cd backend
./run-backend.sh
```

### Frontend

```bash
cd frontend
npm start
```

## Questions?

If you have any questions, please open an issue or contact the maintainers. 