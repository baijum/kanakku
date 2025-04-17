from flask import Blueprint, jsonify, request, current_app, g
from .models import Account, Transaction, db
from .extensions import api_token_required

reports = Blueprint("reports", __name__)


@reports.route("/api/v1/reports/balance", methods=["GET"])
@api_token_required
def get_balance():
    """Get balance report, optionally filtered by account and limited by depth"""
    try:
        account = request.args.get("account")
        depth = request.args.get("depth")

        # Build base query to get account balances
        query = db.session.query(
            Account.name, Account.currency, Account.balance
        ).filter(Account.user_id == g.current_user.id)

        # Filter by account name if provided
        if account:
            query = query.filter(Account.name.like(f"{account}%"))

        # Get all accounts
        accounts = query.all()

        # Parse into hierarchical structure based on account name components
        # For depth limiting, we'll parse the account names and limit display depth
        result = []

        for acct in accounts:
            # Split account name by colon for hierarchical grouping
            components = acct.name.split(":")

            # Limit to specified depth if provided
            display_name = ":".join(components[: int(depth)]) if depth else acct.name

            # Format balance with currency
            balance_str = f"{acct.balance:.2f} {acct.currency}"

            # Add account and balance to result
            result.append(f"{display_name:<40} {balance_str:>15}")

        # Join all lines with newlines to match ledger CLI output format
        output = "\n".join(result)

        return jsonify({"balance": output})
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
        result = []
        for tx in transactions:
            date_str = tx.date.strftime("%Y-%m-%d")
            description = tx.description
            payee = f"Payee: {tx.payee}" if tx.payee else ""
            account = tx.account_name
            amount = f"{tx.amount:.2f} {tx.currency}"

            line = f"{date_str} {description} {payee}\n    {account}    {amount}"
            result.append(line)

        # Join all lines with newlines to match ledger CLI output format
        output = "\n".join(result)

        return jsonify({"register": output})
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
            db.session.query(
                Account.name, Account.currency, Account.balance
            )
            .filter(Account.user_id == g.current_user.id)
            .order_by(Account.name)
            .all()
        )

        # Format results
        result = []
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
                            result.append(f"    {'':<38} {'₹'}{amount:.2f}")
                        else:
                            result.append(f"    {'':<38} {amount:.2f} {currency:>3}")
                    result.append("")  # Empty line between sections

                current_type = account_type
                result.append(f"{current_type}")
                total_by_type = {}

            # Format account balance
            if acct.currency == "INR":
                balance_str = f"₹{acct.balance:.2f}"
            else:
                balance_str = f"{acct.balance:.2f} {acct.currency}"
            result.append(f"    {acct.name:<38} {balance_str:>15}")

            # Track total by currency
            if acct.currency not in total_by_type:
                total_by_type[acct.currency] = 0
            total_by_type[acct.currency] += acct.balance

        # Add final type total
        if current_type is not None:
            for currency, amount in total_by_type.items():
                if currency == "INR":
                    result.append(f"    {'':<38} {'₹'}{amount:.2f}")
                else:
                    result.append(f"    {'':<38} {amount:.2f} {currency:>3}")

        # Join all lines with newlines
        output = "\n".join(result)

        return jsonify({"balance_report": output})
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
            .filter(Account.user_id == g.current_user.id, Account.name.like("Expenses:%"))
            .order_by(Account.name)
            .all()
        )

        # Format results
        result = ["Income"]
        income_total = {}

        for acct in income:
            if acct.currency == "INR":
                balance_str = f"₹{acct.balance:.2f}"
            else:
                balance_str = f"{acct.balance:.2f} {acct.currency}"
            result.append(f"    {acct.name:<38} {balance_str:>15}")

            if acct.currency not in income_total:
                income_total[acct.currency] = 0
            income_total[acct.currency] += acct.balance

        # Add income subtotal
        for currency, amount in income_total.items():
            if currency == "INR":
                result.append(f"    {'':<38} {'₹'}{amount:.2f}")
            else:
                result.append(f"    {'':<38} {amount:.2f} {currency:>3}")

        result.append("")  # Empty line between sections
        result.append("Expenses")
        expense_total = {}

        for acct in expenses:
            if acct.currency == "INR":
                balance_str = f"₹{acct.balance:.2f}"
            else:
                balance_str = f"{acct.balance:.2f} {acct.currency}"
            result.append(f"    {acct.name:<38} {balance_str:>15}")

            if acct.currency not in expense_total:
                expense_total[acct.currency] = 0
            expense_total[acct.currency] += acct.balance

        # Add expense subtotal
        for currency, amount in expense_total.items():
            if currency == "INR":
                result.append(f"    {'':<38} {'₹'}{amount:.2f}")
            else:
                result.append(f"    {'':<38} {amount:.2f} {currency:>3}")

        # Add net income/loss section
        result.append("")  # Empty line
        result.append("Net:")

        # Calculate net income/loss for each currency
        all_currencies = set(list(income_total.keys()) + list(expense_total.keys()))
        for currency in all_currencies:
            income_amt = income_total.get(currency, 0)
            expense_amt = expense_total.get(currency, 0)
            net_amt = income_amt - expense_amt
            if currency == "INR":
                result.append(f"    {'':<38} {'₹'}{net_amt:.2f}")
            else:
                result.append(f"    {'':<38} {net_amt:.2f} {currency:>3}")

        # Join all lines with newlines
        output = "\n".join(result)

        return jsonify({"income_statement": output})
    except Exception as e:
        current_app.logger.error(f"Income statement error: {e}")
        return jsonify({"error": str(e)}), 500
