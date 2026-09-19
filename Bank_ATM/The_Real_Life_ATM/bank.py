from pathlib import Path

from customer import Customer
from account import Account

# Everything resolves against the folder this file lives in, so the program
# runs correctly no matter what the current working directory is (the game,
# for example, may be launched from anywhere).
BASE_DIR = Path(__file__).resolve().parent


class Bank:

    def __init__(self, name, customer_file, transaction_file):
        self.name = name
        self.customer_file = BASE_DIR / customer_file
        self.transaction_file = BASE_DIR / transaction_file
        # Make sure the transaction log's folder exists.
        self.transaction_file.parent.mkdir(parents=True, exist_ok=True)

    def find_customer(self, customer_id):
        if not self.customer_file.exists():
            return None, None

        with open(self.customer_file, "r", encoding="utf-8") as file:
            for line in file:
                # Ignore comments and blank lines.
                if line.startswith("#") or not line.strip():
                    continue

                data = line.strip().split("|")
                stored_id = data[0]

                if stored_id == customer_id:
                    name = data[1]
                    pin = data[2]
                    account_number = data[3]
                    balance = float(data[4])

                    customer = Customer(stored_id, name, pin)
                    account = Account(self.name, account_number, balance)
                    return customer, account

        return None, None

    def update_balance(self, account_number, new_balance):
        """Persist a changed balance back to the customer file.

        The original never wrote balances back, so every run reset to the
        starting amount. This rewrites only the matching account's balance
        field, preserving comments, order and every other field. Written to a
        temp file and swapped in, so a crash can't leave a half-written file.
        """
        if not self.customer_file.exists():
            return False

        lines = self.customer_file.read_text(encoding="utf-8").splitlines(keepends=True)
        changed = False
        for i, line in enumerate(lines):
            if line.startswith("#") or not line.strip():
                continue
            data = line.rstrip("\n").split("|")
            if len(data) >= 5 and data[3] == account_number:
                data[4] = f"{new_balance:.2f}"
                newline = "\n" if line.endswith("\n") else ""
                lines[i] = "|".join(data) + newline
                changed = True
                break

        if not changed:
            return False

        tmp = self.customer_file.with_suffix(self.customer_file.suffix + ".tmp")
        tmp.write_text("".join(lines), encoding="utf-8")
        tmp.replace(self.customer_file)
        return True
