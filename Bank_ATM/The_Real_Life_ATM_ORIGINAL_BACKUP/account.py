from datetime import datetime

class Account:

    def __init__(self, bank_name, account_number, balance):
        self.bank_name = bank_name
        self.account_number = account_number
        self.balance = balance

    def check_balance(self):
        return self.balance

    def deposit(self, amount, transaction_file):

        if amount <= 0:
            print("Amount must be greater than zero.")
            return False
        self.balance += amount

        self.save_transaction(
            "Deposit",
            amount,
            transaction_file
        )

        return True
    def withdraw(self, amount, transaction_file):

        if amount <= 0:
            print("Amount must be greater than zero.")
            return False
        if amount > self.balance:
            print("Insufficient funds.")
            return False
        self.balance -= amount

        self.save_transaction(
            "Withdrawal",
            amount,
            transaction_file 
        )
        return True
    def save_transaction(self, transaction_type, amount, transaction_file):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(transaction_file, "a") as file:

            file.write(
                f"(date_time) | "
                f"(self.bank_name) | "
                f"Account: (self.account_number) | "
                f"(transaction_type) | "
                f"$(amount:.2f) | "
                f"Balance: $(self.balance:.2f)\n"
            )
            