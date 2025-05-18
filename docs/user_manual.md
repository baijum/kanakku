# Kanakku User Manual

## Introduction

Welcome to Kanakku, your personal expense tracking system. Kanakku provides a user-friendly way to manage your personal finances, track expenses, and gain insights into your spending habits. This manual will guide you through the features and functionality of Kanakku to help you make the most of this powerful financial tool.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Accounts](#accounts)
4. [Transactions](#transactions)
5. [Reports](#reports)
6. [Books](#books)
7. [Profile Settings](#profile-settings)
8. [Tips and Best Practices](#tips-and-best-practices)
9. [Bank Transaction Processing](#bank-transaction-processing)

## Getting Started

### Accessing Kanakku

You can access Kanakku through your web browser at the URL provided by your administrator. Kanakku works best on modern browsers like Chrome, Firefox, Safari, or Edge.

### Creating an Account

1. Navigate to the Kanakku login page
2. Click on "Register" to create a new account
3. Fill in your details:
   - Username
   - Email address
   - Password
4. Click "Register" to create your account
5. Wait for account activation (if required by your administrator)

### Logging In

1. Navigate to the Kanakku login page
2. Enter your username and password
3. Click "Login"

### Google Sign-In (Optional)

If enabled on your Kanakku instance:

1. Click "Continue with Google" on the login page
2. Select your Google account or enter your Google credentials
3. Authorize Kanakku to access your Google account information

## Dashboard

The dashboard is your home screen in Kanakku and provides a quick overview of your financial status.

### Key Elements

- **Recent Transactions**: Shows your most recent financial transactions
- **Account Balances**: Displays current balances for your accounts
- **Refresh Button**: Updates the information on your dashboard with the latest data

## Accounts

Accounts in Kanakku represent different sources and destinations for your money, such as checking accounts, credit cards, expense categories, and income sources.

### Types of Accounts

- **Assets**: Represent what you own (checking accounts, savings, investments)
- **Liabilities**: Represent what you owe (credit cards, loans)
- **Expenses**: Categories for spending (food, utilities, entertainment)
- **Income**: Sources of money (salary, interest, gifts)

### Managing Accounts

#### Creating a New Account

1. Navigate to the Accounts section
2. Click "Create Account"
3. Fill in the account details:
   - Name (required)
   - Description (optional)
   - Account Type
   - Opening Balance (if applicable)
4. Click "Create" to add the account

#### Editing an Account

1. Navigate to the Accounts section
2. Find the account you want to edit
3. Click the "Edit" (pencil) icon 
4. Update the account details
5. Click "Save" to apply your changes

#### Deleting an Account

1. Navigate to the Accounts section
2. Find the account you want to delete
3. Click the "Delete" (trash) icon
4. Confirm the deletion when prompted

**Note**: Deleting an account will not delete associated transactions. However, it may affect your financial reports.

## Transactions

Transactions are the core of Kanakku and represent the movement of money between accounts.

### Double-Entry Accounting

Kanakku uses double-entry accounting, which means:
- Every transaction must balance (debits must equal credits)
- Money always moves from one account to another
- This approach ensures accuracy and provides a complete picture of your finances

### Adding a Transaction

1. Navigate to the "Add Transaction" page
2. Fill in the transaction details:
   - Date
   - Payee (who you paid or received money from)
   - Status (optional: cleared, pending, etc.)
3. Add postings (account entries):
   - For each posting, select an account and enter an amount
   - Amounts can be positive (debit) or negative (credit)
   - The sum of all postings must equal zero
4. Click "Add Transaction" to save

#### Example Transactions

**Expense (e.g., Grocery Shopping)**:
- Date: 2023-05-15
- Payee: Grocery Store
- Postings:
  - Expenses:Food: ₹1,000 (positive/debit)
  - Assets:Checking: -₹1,000 (negative/credit)

**Income (e.g., Salary)**:
- Date: 2023-05-01
- Payee: Employer
- Postings:
  - Assets:Checking: ₹50,000 (positive/debit)
  - Income:Salary: -₹50,000 (negative/credit)

**Credit Card Payment**:
- Date: 2023-05-20
- Payee: Credit Card Company
- Postings:
  - Liabilities:Credit Card: ₹15,000 (positive/debit)
  - Assets:Checking: -₹15,000 (negative/credit)

### Viewing Transactions

1. Navigate to the "View Transactions" page
2. Browse your transactions in the table
3. Use filters to narrow down transactions:
   - Date range (start date and end date)
   - Search by payee or description

### Editing and Deleting Transactions

1. On the "View Transactions" page, find the transaction you want to modify
2. Click the "Edit" icon to update the transaction details
3. Click the "Delete" icon to remove the transaction (requires confirmation)

### Exporting Transactions

1. On the "View Transactions" page, click "Export"
2. Select your export format
3. Click "Export" to download your transaction data

## Reports

Kanakku provides various reports to help you understand your financial situation.

### Balance Report

Shows the current balance of each account:
1. Navigate to the Reports section
2. View your account balances organized by account type

### Register Report

Shows a chronological list of transactions:
1. Navigate to the Reports section
2. Select the Register report
3. View transactions with their details

## Books

Kanakku supports multiple books, which allows you to separate different areas of your finances.

### Switching Books

1. Click on the Book Selector in the navigation area
2. Select the book you want to work with
3. All transactions and accounts will now display for the selected book

### Creating a New Book

1. Navigate to the Books section
2. Click "Create Book"
3. Enter the book name and description
4. Click "Create"

## Profile Settings

### Updating Your Profile

1. Click on your username in the top-right corner
2. Select "Profile Settings"
3. Update your information:
   - Display name
   - Email address
   - Password
4. Click "Save Changes"

### Changing Your Password

1. Navigate to Profile Settings
2. Enter your current password
3. Enter and confirm your new password
4. Click "Change Password"

## Tips and Best Practices

### Account Structure

Consider organizing your accounts hierarchically for better reporting:
- Assets:Bank:Checking
- Assets:Bank:Savings
- Expenses:Home:Rent
- Expenses:Home:Utilities
- Expenses:Food:Groceries
- Expenses:Food:Dining

### Regular Reconciliation

Regularly compare your Kanakku balances with actual bank statements to ensure accuracy:
1. Get your latest bank statement
2. Compare the ending balance with your Kanakku balance
3. Mark any discrepancies and correct them

### Consistent Transaction Entry

Develop a consistent approach to entering transactions:
- Enter transactions as they occur or set a regular schedule
- Use consistent payee names for better reporting
- Categorize expenses consistently

### Backing Up Your Data

While Kanakku stores your data securely, you may want to export your data periodically for backup purposes using the export feature.

## Troubleshooting

### Common Issues

**Issue**: Transaction doesn't balance
**Solution**: Ensure that all debits equal all credits (sum equals zero)

**Issue**: Cannot delete an account
**Solution**: You may need to reassign transactions from that account first

**Issue**: Session expired
**Solution**: Log in again to refresh your session token

### Getting Help

If you encounter any issues not covered in this manual, reach out to your administrator or support team for assistance.

## Bank Transaction Processing

Kanakku includes an automated bank transaction processing system that can automatically import transactions from your bank emails.

### Setting Up Bank Email Processing

1. **Configure Email Access**:
   - Set up a Gmail account for receiving bank transaction emails
   - Enable App Password in your Google Account settings
   - Add the following to your `.env` file:
     ```
     GMAIL_USERNAME=your-email@gmail.com
     GMAIL_APP_PASSWORD=your-app-password
     BANK_EMAILS=alerts@axisbank.com,alerts@icicibank.com
     ```

2. **Configure Account Mapping**:
   - Edit `config.toml` to map your bank accounts to ledger accounts:
     ```toml
     [bank-account-map]
     XX1648 = "Assets:Bank:Axis"
     XX0907 = "Liabilities:CC:Axis"
     ```

3. **Configure Expense Categories**:
   - Add merchant-to-category mappings in `config.toml`:
     ```toml
     [expense-account-map]
     "GROCERY STORE" = ["Expenses:Food:Groceries", "Monthly groceries"]
     "RESTAURANT" = ["Expenses:Food:Dining", "Dinner at restaurant"]
     ```

### Running the Transaction Processor

1. **Start the Processor**:
   ```bash
   cd banktransactions
   python main.py
   ```

2. **Monitor Processing**:
   - Check the logs for successful imports
   - Review imported transactions in the Transactions view
   - Verify account balances match your bank statements

### Transaction Processing Features

1. **Automatic Categorization**:
   - Transactions are automatically categorized based on merchant names
   - Categories are mapped to your expense accounts
   - Custom descriptions can be added for better tracking

2. **Account Mapping**:
   - Bank accounts are mapped to your ledger accounts
   - Supports multiple account types (Assets, Liabilities)
   - Handles masked account numbers for security

3. **Email Processing**:
   - Supports multiple bank email formats
   - Handles different transaction types
   - Deduplicates transactions to prevent double entries

### Troubleshooting Bank Transactions

1. **Missing Transactions**:
   - Verify email server connection
   - Check email filters and spam folders
   - Ensure bank emails are being received

2. **Incorrect Categorization**:
   - Review and update merchant mappings in `config.toml`
   - Add new merchants to the expense mapping
   - Adjust category assignments as needed

3. **Account Mapping Issues**:
   - Verify bank account numbers in the mapping
   - Check ledger account names for typos
   - Update mappings for new accounts

### Best Practices

1. **Regular Monitoring**:
   - Check imported transactions daily
   - Verify categorization accuracy
   - Review account balances regularly

2. **Configuration Maintenance**:
   - Keep merchant mappings up to date
   - Add new merchants as needed
   - Review and update account mappings

3. **Data Verification**:
   - Compare imported transactions with bank statements
   - Verify transaction amounts and dates
   - Check category assignments 