"""Simple terminal ATM (the original interface), now on the clean backend.

This still works exactly like before, but the logic now lives in atm_service /
Account / Bank, so the Pygame game (atm_game.py) and this CLI share one backend.
Run the graphical version with:  python atm_game.py
"""
from atm_service import AtmService, ATMError


def main():
    svc = AtmService()
    banks = svc.banks()

    print("====================================")
    print("            ATM MACHINE")
    print("====================================\n")
    print("Select your bank\n")
    for i, (name, _bank) in enumerate(banks, 1):
        print(f"{i}. {name}")

    choice = input("\nEnter your choice: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(banks)):
        print("Invalid bank selection")
        return
    bank_name, bank = banks[int(choice) - 1]

    print(f"\n====================================")
    print(f"            {bank_name}")
    print(f"====================================")

    customer_id = input("\nEnter Customer ID: ")
    customer, account = svc.login(bank, customer_id)
    if customer is None:
        print(f"\nCustomer not found at {bank_name}.")
        return

    print(f"\nWelcome, {customer.name}!")

    # PIN authentication - 3 attempts
    attempts = 0
    while True:
        if svc.verify_pin(customer, input("\nEnter your PIN: ")):
            print("\nAuthentication successful.")
            break
        attempts += 1
        remaining = 3 - attempts
        if attempts == 3:
            print("\nIncorrect PIN.\nMaximum PIN attempts reached.\nTransaction cancelled.")
            return
        print(f"Incorrect PIN.\nYou have {remaining} attempt(s) remaining.")

    print(f"\nBank: {bank_name}")
    print(f"Account: {account.account_number}")
    print(f"Balance: ${account.balance:.2f}")

    print("\n====================================")
    print("           TRANSACTIONS")
    print("====================================")
    print("1. Check Balance")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Exit")

    transaction = input("\nChoose a transaction: ").strip()

    try:
        if transaction == "1":
            print(f"\nYour balance is ${svc.check_balance(account):.2f}")
        elif transaction == "2":
            amount = float(input("Enter deposit amount: $"))
            print(f"\nDeposit successful\nNew balance: ${svc.deposit(account, amount):.2f}")
        elif transaction == "3":
            amount = float(input("Enter withdrawal amount: $"))
            print(f"\nWithdrawal successful.\nNew balance: ${svc.withdraw(account, amount):.2f}")
        elif transaction == "4":
            print("\nThank you for using the ATM.")
        else:
            print("Invalid transaction.")
    except ValueError:
        print("Please enter a valid amount.")
    except ATMError as e:
        print(f"\n{e}")


if __name__ == "__main__":
    main()
