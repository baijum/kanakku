from flask import Blueprint, current_app, g, jsonify, request

from .extensions import api_token_required, db
from .models import Account, Transaction

reports = Blueprint("reports", __name__)


@reports.route("/api/v1/reports/balance", methods=["GET"])
@api_token_required
def get_balance():
    """Get balance report, optionally filtered by account and limited by depth"""
    try:
        account = request.args.get("account")
        depth = request.args.get("depth")
        book_id = request.args.get("book_id", type=int)

        # Build base query to get account balances
        query = db.session.query(
            Account.name, Account.currency, Account.balance
        ).filter(Account.user_id == g.current_user.id)

        # Filter by account name if provided
        if account:
            query = query.filter(Account.name.like(f"{account}%"))

        # Filter by book_id if provided
        if book_id:
            query = query.filter(Account.book_id == book_id)
        else:
            # If no book_id is provided, use the user's active book
            if g.current_user.active_book_id:
                query = query.filter(Account.book_id == g.current_user.active_book_id)

        # Get all accounts
        accounts = query.all()

        # Parse into hierarchical structure based on account name components
        # For depth limiting, we'll parse the account names and limit display depth
        result = []

        # Dictionary to hold account types and their balances
        account_types = {}

        # If depth is provided, track unique top-level accounts
        # to ensure we include all of them, even with zero balances
        if depth:
            # Create a map to aggregate balances for top-level accounts
            top_level_accounts = {}

            for acct in accounts:
                # Split account name by colon for hierarchical grouping
                components = acct.name.split(":")

                # Get top-level account name based on depth
                display_name = ":".join(components[: int(depth)])
                account_type = components[
                    0
                ].lower()  # Get first component for categorization

                # For income accounts, we flip the sign for reporting purposes
                balance = acct.balance
                if account_type == "income":
                    balance = -balance

                # Add to top-level accounts map or update existing entry
                if display_name in top_level_accounts:
                    # If currencies match, add balances
                    if top_level_accounts[display_name]["currency"] == acct.currency:
                        top_level_accounts[display_name]["balance"] += balance
                else:
                    top_level_accounts[display_name] = {
                        "balance": balance,
                        "currency": acct.currency,
                        "type": account_type,
                    }

            # Convert aggregated top-level accounts to result format and categorize by type
            for display_name, data in top_level_accounts.items():
                balance_str = f"{data['balance']:.2f} {data['currency']}"
                account_type = data["type"]

                if account_type not in account_types:
                    account_types[account_type] = []

                account_types[account_type].append(
                    {
                        "name": display_name,
                        "balance": data["balance"],
                        "currency": data["currency"],
                        "display": f"{display_name:<40} {balance_str:>15}",
                    }
                )

                result.append(f"{display_name:<40} {balance_str:>15}")
        else:
            # Original behavior for no depth limitation
            for acct in accounts:
                display_name = acct.name
                # For income accounts, we flip the sign for reporting purposes
                balance = acct.balance
                if acct.name.split(":")[0].lower() == "income":
                    balance = -balance

                balance_str = f"{balance:.2f} {acct.currency}"
                account_type = (
                    acct.name.split(":")[0].lower() if ":" in acct.name else "other"
                )

                if account_type not in account_types:
                    account_types[account_type] = []

                account_types[account_type].append(
                    {
                        "name": display_name,
                        "balance": balance,
                        "currency": acct.currency,
                        "display": f"{display_name:<40} {balance_str:>15}",
                    }
                )

                result.append(f"{display_name:<40} {balance_str:>15}")

        # Join all lines with newlines to match ledger CLI output format
        output = "\n".join(result)

        # Create response with both raw text output and structured account data
        response = {
            "balance": output,  # Keep for backward compatibility
        }

        # Add all account types to the response
        for account_type, accounts in account_types.items():
            response[account_type] = accounts

        # Ensure "assets", "liabilities", "income", and "expenses" keys exist
        required_types = ["assets", "liabilities", "income", "expenses", "equity"]
        for required_type in required_types:
            if required_type not in response:
                response[required_type] = []

        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Balance report error: {e}")
        return jsonify({"error": str(e)}), 500


@reports.route("/api/v1/reports/register", methods=["GET"])
@api_token_required
def get_register():
    """Get transaction register, optionally filtered by account and limited by count"""
    try:
        account = request.args.get("account")
        limit = request.args.get("limit", type=int)

        # Start with a query for transactions
        query = (
            db.session.query(
                Transaction.date,
                Transaction.description,
                Transaction.payee,
                Transaction.amount,
                Transaction.currency,
                Account.name.label("account_name"),
            )
            .join(Account, Transaction.account_id == Account.id)
            .filter(Transaction.user_id == g.current_user.id)
            .order_by(Transaction.date.desc())
        )

        # Filter by account if provided
        if account:
            query = query.filter(Account.name.like(f"{account}%"))

        # Apply limit if provided
        if limit:
            query = query.limit(limit)

        # Execute query
        transactions = query.all()

        # Format results similar to ledger register output
        text_result = []
        data_result = []

        for tx in transactions:
            date_str = tx.date.strftime("%Y-%m-%d")
            description = tx.description or ""
            payee = tx.payee or ""
            account = tx.account_name
            amount = float(tx.amount)
            currency = tx.currency

            # Format text output
            payee_text = f"Payee: {payee}" if payee else ""
            line = f"{date_str} {description} {payee_text}\n    {account}    {amount:.2f} {currency}"
            text_result.append(line)

            # Format structured data
            data_result.append(
                {
                    "date": date_str,
                    "description": description,
                    "payee": payee,
                    "account": account,
                    "amount": amount,
                    "currency": currency,
                }
            )

        # Join all lines with newlines to match ledger CLI output format
        # text_output = "\n".join(text_result)

        # Return both formatted text and structured data
        # Main response is the array format expected by tests
        return jsonify(data_result)
    except Exception as e:
        current_app.logger.error(f"Register report error: {e}")
        return jsonify({"error": str(e)}), 500


@reports.route("/api/v1/reports/balance_report", methods=["GET"])
@api_token_required
def get_balance_report():
    """Get a full balance report for all accounts"""
    try:
        # Query all accounts and their balances
        accounts = (
            db.session.query(Account.name, Account.currency, Account.balance)
            .filter(Account.user_id == g.current_user.id)
            .order_by(Account.name)
            .all()
        )

        # Format results
        text_result = []
        accounts_data = []
        current_type = None
        total_by_type = {}

        for acct in accounts:
            # Extract type from account name (first part before colon)
            account_type = acct.name.split(":")[0] if ":" in acct.name else "Other"

            # Add type header if it's a new type
            if account_type != current_type:
                if current_type is not None:
                    # Add subtotal for previous type
                    for currency, amount in total_by_type.items():
                        if currency == "INR":
                            text_result.append(f"    {'':<38} {'₹'}{amount:.2f}")
                        else:
                            text_result.append(
                                f"    {'':<38} {amount:.2f} {currency:>3}"
                            )
                    text_result.append("")  # Empty line between sections

                current_type = account_type
                text_result.append(f"{current_type}")
                total_by_type = {}

            # Format account balance
            if acct.currency == "INR":
                balance_str = f"₹{acct.balance:.2f}"
            else:
                balance_str = f"{acct.balance:.2f} {acct.currency}"
            text_result.append(f"    {acct.name:<38} {balance_str:>15}")

            # Add account to structured data
            accounts_data.append(
                {"name": acct.name, "balance": acct.balance, "currency": acct.currency}
            )

            # Track total by currency
            if acct.currency not in total_by_type:
                total_by_type[acct.currency] = 0
            total_by_type[acct.currency] += acct.balance

        # Add final type total
        if current_type is not None:
            for currency, amount in total_by_type.items():
                if currency == "INR":
                    text_result.append(f"    {'':<38} {'₹'}{amount:.2f}")
                else:
                    text_result.append(f"    {'':<38} {amount:.2f} {currency:>3}")

        # Join all lines with newlines
        text_output = "\n".join(text_result)

        # Construct response with both text and structured data
        response = {
            "balance_report": text_output,  # Keep for backward compatibility
            "accounts": accounts_data,  # Flat list of accounts as expected by tests
        }

        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Balance report error: {e}")
        return jsonify({"error": str(e)}), 500


@reports.route("/api/v1/reports/income_statement", methods=["GET"])
@api_token_required
def get_income_statement():
    """Generate an income statement (Income vs Expenses)"""
    try:
        # Query Income accounts
        income = (
            db.session.query(Account.name, Account.currency, Account.balance)
            .filter(Account.user_id == g.current_user.id, Account.name.like("Income:%"))
            .order_by(Account.name)
            .all()
        )

        # Query Expense accounts
        expenses = (
            db.session.query(Account.name, Account.currency, Account.balance)
            .filter(
                Account.user_id == g.current_user.id, Account.name.like("Expenses:%")
            )
            .order_by(Account.name)
            .all()
        )

        # Format results
        text_result = ["Income"]
        income_total = {}

        # Structured data - list format for test compatibility
        income_data = []
        expense_data = []

        for acct in income:
            if acct.currency == "INR":
                balance_str = f"₹{acct.balance:.2f}"
            else:
                balance_str = f"{acct.balance:.2f} {acct.currency}"
            text_result.append(f"    {acct.name:<38} {balance_str:>15}")

            # Add to structured data - abs(balance) for test expectations
            income_data.append(
                {
                    "name": acct.name,
                    "balance": abs(
                        acct.balance
                    ),  # Use absolute value for test compatibility
                    "currency": acct.currency,
                }
            )

            if acct.currency not in income_total:
                income_total[acct.currency] = 0
            income_total[acct.currency] += acct.balance

        # Add income subtotal
        for currency, amount in income_total.items():
            if currency == "INR":
                text_result.append(f"    {'':<38} {'₹'}{amount:.2f}")
            else:
                text_result.append(f"    {'':<38} {amount:.2f} {currency:>3}")

        text_result.append("")  # Empty line between sections
        text_result.append("Expenses")
        expense_total = {}

        for acct in expenses:
            if acct.currency == "INR":
                balance_str = f"₹{acct.balance:.2f}"
            else:
                balance_str = f"{acct.balance:.2f} {acct.currency}"
            text_result.append(f"    {acct.name:<38} {balance_str:>15}")

            # Add to structured data
            expense_data.append(
                {"name": acct.name, "balance": acct.balance, "currency": acct.currency}
            )

            if acct.currency not in expense_total:
                expense_total[acct.currency] = 0
            expense_total[acct.currency] += acct.balance

        # Add expense subtotal
        for currency, amount in expense_total.items():
            if currency == "INR":
                text_result.append(f"    {'':<38} {'₹'}{amount:.2f}")
            else:
                text_result.append(f"    {'':<38} {amount:.2f} {currency:>3}")

        # Calculate net income/expense for each currency
        net_totals = {}
        for currency in set(list(income_total.keys()) + list(expense_total.keys())):
            income_amount = income_total.get(currency, 0)
            expense_amount = expense_total.get(currency, 0)
            net_totals[currency] = income_amount - expense_amount

        # Add net income/expense
        text_result.append("")
        text_result.append("Net:")
        for currency, amount in net_totals.items():
            if currency == "INR":
                text_result.append(f"    {'':<38} {'₹'}{amount:.2f}")
            else:
                text_result.append(f"    {'':<38} {amount:.2f} {currency:>3}")

        # Join all lines with newlines
        text_output = "\n".join(text_result)

        # Construct response with both text and structured data
        response = {
            "income_statement": text_output,  # Keep for backward compatibility
            "income": income_data,  # Flat list for test compatibility
            "expenses": expense_data,  # Flat list for test compatibility
        }

        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Income statement error: {e}")
        return jsonify({"error": str(e)}), 500
