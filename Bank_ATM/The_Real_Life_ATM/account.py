from datetime import datetime


class ATMError(Exception):
    """A domain error the interface can show to the user.

    The backend never prints. It raises this instead, so the front end
    (CLI, Pygame game, or a future web UI) decides how to display the reason.
    """


class Account:

    def __init__(self, bank_name, account_number, balance):
        self.bank_name = bank_name
        self.account_number = account_number
        self.balance = balance

    def check_balance(self):
        return self.balance

    def deposit(self, amount, transaction_file):
        if amount <= 0:
            raise ATMError("Amount must be greater than zero.")

        self.balance += amount
        self.save_transaction("Deposit", amount, transaction_file)
        return self.balance

    def withdraw(self, amount, transaction_file):
        if amount <= 0:
            raise ATMError("Amount must be greater than zero.")
        if amount > self.balance:
            raise ATMError("Insufficient funds.")

        self.balance -= amount
        self.save_transaction("Withdrawal", amount, transaction_file)
        return self.balance

    def save_transaction(self, transaction_type, amount, transaction_file):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # NOTE: the original used ( ) instead of { } here, so it logged the
        # literal text rather than the values. Fixed to real f-string fields.
        with open(transaction_file, "a", encoding="utf-8") as file:
            file.write(
                f"{date_time} | "
                f"{self.bank_name} | "
                f"Account: {self.account_number} | "
                f"{transaction_type} | "
                f"${amount:.2f} | "
                f"Balance: ${self.balance:.2f}\n"
            )
