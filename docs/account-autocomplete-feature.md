# Account Auto-Completion Feature

## Overview

The account auto-completion feature enhances the user experience when entering Ledger CLI-style account names in transaction search. It provides intelligent suggestions based on existing account names in the user's active book.

## Features

### 1. Activation Trigger
- Auto-completion activates only when the user types at least one colon (`:`) character
- This prevents unnecessary API calls for general search terms
- Follows Ledger CLI convention where account names use colons as separators

### 2. Hierarchical Suggestions
The system provides two types of suggestions:

#### Exact Matches
- Complete account names that start with the entered prefix
- Example: For prefix `Assets:Bank:`, returns `Assets:Bank:Checking`, `Assets:Bank:Savings`

#### Next Segment Suggestions
- Suggests the next hierarchical level in account names
- Example: For prefix `Assets:`, suggests `Assets:Bank` (next segment) in addition to full matches

### 3. Case-Insensitive Matching
- Searches are case-insensitive for better user experience
- `assets:` will match `Assets:Bank:Checking`

### 4. Performance Optimizations
- Debounced API calls (300ms delay) to reduce server load
- Configurable result limit (default: 10 suggestions)
- Server-side filtering for efficiency

## Implementation Details

### Backend API Endpoint

```
GET /api/v1/accounts/autocomplete
```

**Parameters:**
- `prefix` (string): Account name prefix (must contain `:`)
- `limit` (integer): Maximum suggestions to return (default: 20)

**Response:**
```json
{
  "suggestions": ["Assets:Bank:Checking", "Assets:Bank:Savings", "Assets:Bank"],
  "prefix": "Assets:Bank:"
}
```

### Frontend Component

The `AccountAutocomplete` component wraps MUI's `Autocomplete` with custom logic:

- **Debounced API calls**: Prevents excessive requests during typing
- **Loading indicators**: Shows spinner during API requests
- **Error handling**: Gracefully handles API failures
- **Customizable props**: Supports all standard TextField props

## Usage Examples

### Basic Usage in ViewTransactions

```jsx
import AccountAutocomplete from './AccountAutocomplete';

<AccountAutocomplete
  value={searchTerm}
  onChange={setSearchTerm}
  label="Search transactions..."
  placeholder="Search by description, payee, amount, status, or account"
  helperText="Type ':' for account suggestions"
/>
```

### Custom Configuration

```jsx
<AccountAutocomplete
  value={searchValue}
  onChange={handleChange}
  label="Account Search"
  disabled={isLoading}
  fullWidth={false}
/>
```

## User Experience Flow

1. **User starts typing**: Regular text input behavior
2. **User types colon**: Auto-completion activates
3. **Suggestions appear**: Dropdown shows matching account names
4. **User selects suggestion**: Account name is auto-filled
5. **User continues typing**: More specific suggestions appear

## Example Scenarios

### Scenario 1: Building Account Path
```
User types: "A"           → No suggestions
User types: "Assets:"     → Shows: ["Assets:Bank:Checking", "Assets:Bank:Savings", "Assets:Cash", "Assets:Bank"]
User types: "Assets:B"    → Shows: ["Assets:Bank:Checking", "Assets:Bank:Savings", "Assets:Bank"]
User types: "Assets:Bank:" → Shows: ["Assets:Bank:Checking", "Assets:Bank:Savings"]
```

### Scenario 2: Expense Categories
```
User types: "Expenses:"        → Shows: ["Expenses:Food:Restaurant", "Expenses:Food:Groceries", "Expenses:Transport", "Expenses:Food"]
User types: "Expenses:Food:"   → Shows: ["Expenses:Food:Restaurant", "Expenses:Food:Groceries"]
```

## Technical Architecture

### Backend Logic
1. **Input validation**: Ensures prefix contains colon
2. **Account filtering**: Finds accounts matching prefix (case-insensitive)
3. **Segment generation**: Creates next-level suggestions
4. **Result combination**: Merges exact matches with segment suggestions
5. **Sorting and limiting**: Alphabetical sort with configurable limit

### Frontend Logic
1. **Input monitoring**: Watches for colon character
2. **Debounced requests**: Delays API calls during rapid typing
3. **State management**: Handles suggestions, loading, and errors
4. **UI rendering**: Shows dropdown with suggestions and loading states

## Testing

### Backend Tests
- Prefix validation (requires colon)
- Hierarchical suggestion generation
- Case-insensitive matching
- Result limiting
- Error handling

### Frontend Tests
- Component rendering
- API call triggering
- Suggestion display
- User interaction handling
- Error state management
- Loading state indication

## Configuration

### Backend Configuration
```python
# In accounts.py
limit = request.args.get("limit", 20, type=int)  # Default limit
```

### Frontend Configuration
```javascript
// In AccountAutocomplete.jsx
const fetchSuggestions = useCallback(
  debounce(async (searchValue) => {
    // API call with configurable limit
    const response = await axiosInstance.get('/api/v1/accounts/autocomplete', {
      params: {
        prefix: searchValue,
        limit: 10  // Configurable limit
      }
    });
  }, 300),  // Configurable debounce delay
  []
);
```

## Future Enhancements

1. **Caching**: Client-side caching of suggestions for better performance
2. **Fuzzy matching**: Support for typos and partial matches
3. **Recent accounts**: Prioritize recently used accounts in suggestions
4. **Keyboard navigation**: Enhanced keyboard shortcuts for suggestion selection
5. **Custom separators**: Support for different account hierarchy separators

## Integration Points

The auto-completion feature integrates with:
- **Transaction search**: Primary use case in ViewTransactions component
- **Account management**: Could be extended to account creation forms
- **Report filtering**: Potential use in report generation interfaces
- **Import/export**: Could assist in account mapping during data import 