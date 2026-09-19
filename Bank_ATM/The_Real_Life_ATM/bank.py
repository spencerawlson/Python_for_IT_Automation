from customer import Customer
from account import Account
from pathlib import Path

class Bank:

    def __init__(self, name, customer_file, transaction_file):
        self.name = name
        base_dir = Path(__file__).resolve().parent
        self.customer_file = customer_file
        self.transaction_file = transaction_file

    def find_customer(self, customer_id):
        with open(self.customer_file, "r") as file:

            for line in file:
                # Ignore comments and blank lines
                if line.startswith("#") or not line.strip():
                    continue

                data = line.strip().split("|")
                stored_id = data[0]

                if stored_id == customer_id:

                    name = data[1]
                    pin = data[2]
                    account_number = data[3]
                    balance = float(data[4])

                    customer = Customer(
                        stored_id,
                        name,
                        pin
                    )
                    account = Account(
                        self.name,
                        account_number,
                        balance
                    )

                    return customer, account
        return None, None