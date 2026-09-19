"""ATM service layer — the clean seam between the logic and any interface.

This is the backend the interfaces sit on top of. It never prints and never
asks for input: it returns data and results, and raises ATMError with a reason
when something can't be done. The terminal CLI (atm.py), the Pygame game
(atm_game.py) and a future web API all drive these same methods.

    svc = AtmService()
    svc.banks()                      -> [("CIBC", <Bank>), ...]
    svc.login(bank, "C001")          -> Customer | None
    svc.verify_pin(customer, "1234") -> bool
    svc.deposit(account, 100)        -> new balance   (persists + logs)
    svc.withdraw(account, 60)        -> new balance   (persists + logs)
    svc.dispense(60)                 -> {20: 3}        (bills for the animation)
"""
from bank import Bank
from account import Account, ATMError

__all__ = ["AtmService", "ATMError", "Account"]

# Denominations the dispenser stocks, largest first (Canadian bills).
DENOMINATIONS = [100, 50, 20, 10, 5]


class AtmService:
    def __init__(self):
        # The three banks on this ATM network. Paths are relative to the
        # project folder; Bank resolves them against its own location.
        self._banks = [
            Bank("CIBC", "banks/cibc.txt", "transactions/cibc_transactions.txt"),
            Bank("RBC", "banks/rbc.txt", "transactions/rbc_transactions.txt"),
            Bank("Bank of Montreal", "banks/bmo.txt", "transactions/bmo_transactions.txt"),
        ]

    def banks(self):
        """Return [(display_name, Bank), ...] for the bank-select screen."""
        return [(b.name, b) for b in self._banks]

    def login(self, bank, customer_id):
        """Look a customer up. Returns (Customer, Account) or (None, None).

        Stashes the resolved bank on the account so deposit/withdraw can
        persist and log without the caller passing files around.
        """
        customer, account = bank.find_customer(customer_id.strip())
        if account is not None:
            account._bank = bank  # used by deposit/withdraw below
        return customer, account

    def verify_pin(self, customer, pin):
        return customer.verify_pin(pin)

    def check_balance(self, account):
        return account.check_balance()

    def deposit(self, account, amount):
        """Deposit, persist the new balance, log it. Raises ATMError on bad input."""
        bank = account._bank
        new_balance = account.deposit(amount, str(bank.transaction_file))
        bank.update_balance(account.account_number, new_balance)
        return new_balance

    def withdraw(self, account, amount):
        """Withdraw, persist, log. Raises ATMError on bad input / insufficient funds."""
        bank = account._bank
        new_balance = account.withdraw(amount, str(bank.transaction_file))
        bank.update_balance(account.account_number, new_balance)
        return new_balance

    def dispense(self, amount):
        """Break an amount into physical bills, largest first.

        Returns {denomination: count}. The game uses this to animate the exact
        bills sliding out of the tray. Amounts must be a whole multiple of the
        smallest note ($5); the interface enforces that before calling.
        """
        remaining = int(round(amount))
        bills = {}
        for note in DENOMINATIONS:
            if remaining >= note:
                count, remaining = divmod(remaining, note)
                if count:
                    bills[note] = count
        return bills

    def history(self, bank, limit=8):
        """Return the last `limit` transaction-log lines for a receipt/history view."""
        path = bank.transaction_file
        if not path.exists():
            return []
        lines = [ln.rstrip("\n") for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        return lines[-limit:]
