# Fix: PostgreSQL tsquery Special Characters Issue

## Problem Description

When users typed search terms containing special characters (particularly colons `:`) in the transaction search field, they would see the error message "Unable to load transactions. Check your connection." even though there were matching account names available.

### Specific Issue
- **Trigger**: Typing "Assets:" in the transaction search field
- **Expected**: Empty search results (no transactions match "Assets:")
- **Actual**: Network error message displayed
- **Root Cause**: PostgreSQL `to_tsquery()` function failing due to invalid syntax

## Root Cause Analysis

### The Problem Chain
1. User types "Assets:" in search field
2. Frontend sends search request to `/api/v1/transactions?search=Assets:`
3. Backend processes search term for PostgreSQL Full-Text Search (FTS)
4. Search term "Assets:" becomes "Assets::*" in tsquery (double colon)
5. PostgreSQL `to_tsquery('english', 'Assets::*')` fails due to invalid `::` syntax
6. Backend throws exception, returns 500 error
7. Frontend interprets 500 error as network error
8. User sees "Unable to load transactions. Check your connection."

### Code Location
**File**: `backend/app/transactions.py`
**Function**: `get_transactions()`
**Lines**: 220-240

**Problematic Code**:
```python
# Convert search term to tsquery with prefix matching for last word
search_words = search_term.split()
if search_words:
    tsquery_parts = []
    for i, word in enumerate(search_words):
        if i == len(search_words) - 1:  # Last word gets prefix matching
            tsquery_parts.append(f"{word}:*")  # ❌ Creates "Assets::*"
        else:
            tsquery_parts.append(word)
    
    search_query = ' & '.join(tsquery_parts)
    query = query.filter(
        Transaction.search_vector.op('@@')(
            func.to_tsquery('english', search_query)  # ❌ Fails here
        )
    )
```

## Solution Implemented

### 1. Input Sanitization
Added sanitization to remove special characters that break PostgreSQL tsquery:

```python
# Sanitize word by removing special characters that break tsquery
# Keep alphanumeric characters and basic punctuation
sanitized_word = ''.join(c for c in word if c.isalnum() or c in '-_')
if sanitized_word:  # Only add non-empty words
    if i == len(search_words) - 1:  # Last word gets prefix matching
        tsquery_parts.append(f"{sanitized_word}:*")
    else:
        tsquery_parts.append(sanitized_word)
```

### 2. Graceful Fallback
Added try-catch block to fall back to basic text search if tsquery fails:

```python
try:
    query = query.filter(
        Transaction.search_vector.op('@@')(
            func.to_tsquery('english', search_query)
        )
    )
except Exception as e:
    # If tsquery fails, fall back to basic text search
    current_app.logger.warning(f"FTS query failed, falling back to basic search: {e}")
    search_filter = f"%{search_term}%"
    query = query.filter(
        or_(
            Transaction.description.ilike(search_filter),
            Transaction.payee.ilike(search_filter),
            Transaction.currency.ilike(search_filter)
        )
    )
```

### 3. Empty Query Protection
Added check to only proceed with valid search terms:

```python
if tsquery_parts:  # Only proceed if we have valid search terms
    search_query = ' & '.join(tsquery_parts)
    # ... rest of the logic
```

## Testing

### Test Cases Added
Created comprehensive test in `backend/tests/test_search.py`:

```python
def test_search_with_special_characters(self, authenticated_client, user, app):
    """Test search with special characters like colons doesn't cause server errors"""
    special_search_terms = [
        "Assets:",
        "Assets:Bank:",
        "Expenses:Food:",
        "test:with:colons",
        "search@with#symbols",
        "term&with|operators",
        "Assets::double",
    ]
    
    for search_term in special_search_terms:
        response = authenticated_client.get(f"/api/v1/transactions?search={search_term}")
        # Should return 200 (success) even if no results found, not 500 (server error)
        assert response.status_code == 200
```

### Verification
- ✅ All existing search tests pass
- ✅ New special character test passes
- ✅ Frontend AccountAutocomplete tests pass
- ✅ Search terms with colons now return 200 (success) instead of 500 (error)

## Impact

### Before Fix
- Search terms with special characters caused server errors
- Users saw confusing "network connection" error messages
- Poor user experience when typing account names with colons

### After Fix
- Search terms with special characters work correctly
- Empty results show appropriate "No transactions found" message
- Graceful fallback ensures search always works
- Better user experience for Ledger CLI-style account names

## Related Components

### Account Autocomplete Feature
This fix also benefits the account autocomplete feature implemented in the same session:
- **File**: `frontend/src/components/AccountAutocomplete.jsx`
- **Purpose**: Provides autocomplete for Ledger CLI-style account names
- **Benefit**: Users can now type "Assets:" and get both:
  1. Account name suggestions (from autocomplete API)
  2. Transaction search results (now working correctly)

## Prevention

### Code Review Checklist
- [ ] Test search functionality with special characters
- [ ] Verify PostgreSQL tsquery syntax when building dynamic queries
- [ ] Add input sanitization for user-provided search terms
- [ ] Include graceful fallback mechanisms for complex queries

### Monitoring
- Monitor backend logs for "FTS query failed, falling back to basic search" warnings
- Track search API error rates to catch similar issues early

## Lessons Learned

1. **Input Validation**: Always sanitize user input before using in database queries
2. **Graceful Degradation**: Provide fallback mechanisms for complex features
3. **Error Handling**: Distinguish between network errors and application logic errors
4. **Testing**: Include edge cases with special characters in test suites
5. **User Experience**: Error messages should be accurate and helpful

## Files Modified

1. `backend/app/transactions.py` - Fixed PostgreSQL tsquery handling
2. `backend/tests/test_search.py` - Added comprehensive test coverage
3. `frontend/src/components/ViewTransactions.js` - Improved error handling (separate issue)
4. `fixes/postgresql-tsquery-special-characters-fix.md` - This documentation

## Future Improvements

1. **Enhanced Sanitization**: Consider more sophisticated input cleaning
2. **Search Optimization**: Improve search relevance for partial matches
3. **User Feedback**: Provide better feedback when falling back to basic search
4. **Performance**: Monitor impact of fallback searches on performance 