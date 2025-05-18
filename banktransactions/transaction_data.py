import os

from config_reader import load_config

def construct_transaction_data(transaction):
    """
    Construct transaction data from transaction details.
    """

    config_file = os.getenv("CONFIG_FILE_PATH")
    config = load_config(config_file)
    bank_account_map = config.get('bank-account-map', {})
    expense_account_map = config.get('expense-account-map', {})

    recipient = expense_account_map.get(transaction["recipient"], ['Expenses:Groceries', "XXX"])
    transaction_data = {
        "amount": transaction["amount"],
        "transaction_date": transaction["date"],
        "transaction_time": transaction.get("transaction_time", "Unknown"),
        "from_account": bank_account_map.get(transaction["account_number"], 'Assets:Bank:Axis'),
        "to_account": recipient[0],
        "recipient_name": transaction["recipient"]+" "+recipient[1],
    }
    return transaction_data