# Kanakku FAQ

## General Questions

### What is Kanakku?
Kanakku is a personal expense tracking system that helps you manage your finances using double-entry accounting principles. It allows you to track your income, expenses, assets, and liabilities in one place.

### What does "Kanakku" mean?
"Kanakku" means "accounts" in Tamil, reflecting the application's purpose as an accounting tool.

### Is my financial data secure?
Yes. Kanakku uses JWT-based authentication and industry-standard security practices to protect your data. Your financial information is only accessible to your account.

## Account Management

### How do I reset my password?
1. On the login page, click "Forgot Password"
2. Enter your registered email address
3. Check your email for password reset instructions
4. Follow the link to create a new password

### Can I use Kanakku on my mobile device?
Yes, Kanakku features a responsive design that works on desktops, tablets, and smartphones.

### How do I change my email address?
Go to Profile Settings and update your email address in your profile information.

## Financial Concepts

### What is double-entry accounting?
Double-entry accounting is a system where every transaction affects at least two accounts and the sum of debits equals the sum of credits. This ensures your books always balance and provides a complete picture of your finances.

### What's the difference between debit and credit?
In Kanakku:
- A debit (positive amount) increases asset and expense accounts, or decreases liability and income accounts
- A credit (negative amount) decreases asset and expense accounts, or increases liability and income accounts

### How should I structure my accounts?
We recommend using hierarchical account names with colons as separators:
- Assets:Bank:Checking
- Expenses:Housing:Rent
- Income:Salary

This structure allows for more detailed reporting and better organization.

## Transactions

### Why won't my transaction save?
The most common reason is that the transaction doesn't balance (sum to zero). Check that your debits and credits are equal.

### How do I record a transfer between accounts?
Record it as a transaction with two postings:
1. A debit (positive amount) from the receiving account
2. A credit (negative amount) from the sending account

### Can I import transactions from my bank?
Kanakku currently doesn't support direct bank imports. You'll need to enter transactions manually.

### How do I edit or delete a transaction?
Go to "View Transactions," find the transaction, and use the edit (pencil) or delete (trash) icons.

## Books

### What are "books" in Kanakku?
Books allow you to maintain separate sets of accounts. You might use different books for personal finances, a small business, or tracking expenses for a specific project.

### How do I switch between books?
Use the Book Selector in the navigation area to switch between your books.

### Can I transfer data between books?
No, each book is separate. Transactions cannot be moved between books.

## Reporting

### What reports are available?
Kanakku provides:
- Balance reports (showing account balances)
- Transaction registers (showing transaction history)

### Can I customize reports?
You can filter reports by date range and specific accounts.

### Can I export reports?
Yes, you can export your transactions data for use in other applications.

## Troubleshooting

### Why am I seeing "Session expired"?
Your authentication token has expired. Simply log in again to continue.

### My balances don't match my bank account. What should I do?
1. Check for missing transactions
2. Verify transaction amounts
3. Ensure transactions are recorded in the correct accounts
4. Add adjustment transactions if needed to reconcile

### How do I report a bug or request a feature?
Contact your system administrator or support team with detailed information about the issue or feature request.

## Data Management

### How do I back up my data?
You can export your transactions from the "View Transactions" page. We recommend doing this regularly.

### Is there a limit to how many transactions I can have?
Kanakku is designed to handle many years of transactions efficiently.

### Can I delete all my data and start over?
There's no built-in "reset" feature. You would need to delete transactions and accounts individually or ask your administrator for assistance. 