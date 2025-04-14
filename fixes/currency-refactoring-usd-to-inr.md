# Currency Refactoring: USD to INR

## Issue
The application was initially built using US Dollar (USD) as the default currency. We needed to refactor to use Indian Rupee (INR) as the default currency, with the symbol ₹ displayed to the left of the amount.

## Solution
We implemented a comprehensive refactoring across the codebase:

1. **Database Models**:
   - Changed default currency from 'USD' to 'INR' in Account and Transaction models
   - Updated all relevant database operations to use 'INR' as the default

2. **Backend API**:
   - Modified transaction creation and updating endpoints to use 'INR' as default currency
   - Updated reports to format INR amounts with the ₹ symbol on the left side
   - Updated all test fixtures and test cases to use 'INR'

3. **Frontend Components**:
   - Updated AddTransaction component to use ₹ as the default currency symbol
   - Modified EditTransaction component to use 'INR' as the default currency
   - Enhanced Dashboard display to show ₹ symbol to the left of amounts for INR currency

## Implementation Notes
- Currency detection was added to format amounts differently based on currency (₹ symbol on left for INR)
- Currency code 'INR' is stored in the database, with presentation logic on the frontend
- Tests were updated to ensure all functionality works with the new currency

## Challenges Overcome
- Ensuring consistent display of currency symbols across reports and transaction listings
- Handling different formatting rules between currencies (symbol position)
- Maintaining backward compatibility with existing data

This refactoring allows the application to properly support Indian Rupee as the default currency while maintaining support for other currencies if needed. 