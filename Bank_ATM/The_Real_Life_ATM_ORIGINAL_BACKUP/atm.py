from bank import Bank

def main():

    # -----------------------------------------
    # Create the banks
    # -----------------------------------------

    cibc = Bank(
        "CIBC",
        "banks/cibc.txt",
        "transactions/cibc_transactions.txt"
    )

    rbc = Bank(
        "RBC",
        "banks/rbc.txt",
        "transactions/rbc_transactions.txt"
    )
    bmo = Bank(
        "Bank of Montreal",
        "banks/bmo.txt",
        "transactions/bmo_transactions.txt"
    )

    # -------------------------------------------
    # Select the bank
    # -------------------------------------------

    print("====================================")
    print("            ATM MACHINE")
    print("====================================")

    print()
    print('Select your bank')
    print()
    print("1. CIBC")
    print('2. RBC')
    print('3. Bank of Montreal')

    choice =input("\nEnter your choice: ")

    if choice == "1":
        bank = cibc
    elif choice == "2":
        bank = rbc
    elif choice == "3":
        bank = bmo
    else:
        print("Invalid bank selection")
        return

    # -------------------------------------------
    # Customer ID
    # -------------------------------------------

    print()
    print("====================================")
    print(f"            {bank.name}")
    print("====================================")

    customer_id = input("\nEnter Customer ID: ")

    # -------------------------------------------
    # Find customer in selected bank
    # -------------------------------------------

    customer, account = bank.find_customer(customer_id)

    if customer is None:
        print()
        print(f"Customer not found at {bank.name}.")
        return

    # -------------------------------------------
    # Welcome customer
    # -------------------------------------------

    print()
    print(f"Welcome, {customer.name}!")

    # -------------------------------------------
    # PIN Authentication - 3 attemps
    # -------------------------------------------

    attempts = 0

    while True:

        entered_pin = input("\nEnter your PIN: ")

        if customer.verify_pin(entered_pin):
            print("\nAuthenticaton successful.")
            break

        attempts += 1
        remaining = 3 - attempts

        if attempts == 3:
            print()
            print("Incorrect PIN.")
            print("Maximum PIN attempts reached.")
            print("Transaction cancelled.")
            return
        else:
            print("Incorrect PIN.")
            print(f"You have {remaining} attempt(s) remaining.")
    # -------------------------------------------
    # Authentication Successful
    # -------------------------------------------

    print()
    print(f"Bank: {bank.name}")
    print(f"Account: {account.account_number}")
    print(f"Balance: ${account.balance:.2f}")

    # -------------------------------------------
    # Transaction menu
    # -------------------------------------------

    print()
    print("====================================")
    print("           TRANSACTIONS")
    print("====================================")

    print("1. Check Balance")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Exit")

    transaction = input("\nChoose a transaction: ")

    if transaction == "1":

        print()
        print(f"Your balance is ${account.check_balance():.2f}")

    elif transaction == "2":

        try:
            amount = float(
                input("Enter deposit amount: $")
            )

            if account.deposit(
                amount, bank.transaction_file
            ):
                print()
                print("Deposit sucessful")
                print(f"New balance: ${account.balance:.2f}")

        except ValueError:
            print("Please enter a valid amount.")

    elif transaction == "3":

        try:
            amount = float(
                input("Enter withdrawal amount: $")
            )

            if account.withdraw(
                amount,
                bank.transaction_file
            ):
                print()
                print("Withdrawal successful.")
                print(f"New balance: ${account.balance:.2f}")
        except ValueError:
            print("Please enter a valid amount.")

    elif transaction == "4":

        print()
        print("Thank you for using the ATM.")

    else:
        print("Invalid transaction.")

# -------------------------------------------
# Program entry point
# -------------------------------------------

if __name__ == "__main__":
    main() 