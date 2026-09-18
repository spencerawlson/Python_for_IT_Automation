
# ATM BANKING SYSTEM

def select_bank():
    print('Welcome to the ATM Banking System!')
    print('1 - CIBC')
    print('2 - RBC')
    print('3 - Bank of Montreal')

    while True:
        bank = input('Select your bank: ')

        if bank == '1':
            return 'CIBC'
        elif bank == '2':
            return 'RBC'
        elif bank == '3':
            return 'Bank of Montreal'
        else:
            print('Invalid bank.')


def verify_pin():
    pin = input('Please choose a PIN: ')

    for attempt in range(3):
        customer_pin = input('Enter your PIN: ')

        if customer_pin == pin:
            print('PIN accepted!')
            return True

        print('Incorrect PIN.')
        print(f'{2 - attempt} attempts remaining.')

    print('Account BLOCKED.')
    return False


def deposit(balance, history):
    amount = float(input('Deposit amount: '))

    if amount <= 0:
        print('Invalid amount.')
    else:
        balance += amount
        history.append(f'Deposited ${amount:.2f}')
        print(f'New balance: ${balance:.2f}')

    return balance


def withdraw(balance, history):
    amount = float(input('Withdrawal amount: '))

    if amount <= 0:
        print('Invalid amount.')
    elif amount > balance:
        print('Insufficient funds.')
    else:
        balance -= amount
        history.append(f'Withdrew ${amount:.2f}')
        print(f'New balance: ${balance:.2f}')

    return balance


def direct_deposit():
    print('\n1 - CIBC')
    print('2 - RBC')
    print('3 - Bank of Montreal')

    bank = input('Select receiving bank: ')

    if bank == '1':
        bank = 'CIBC'
    elif bank == '2':
        bank = 'RBC'
    elif bank == '3':
        bank = 'Bank of Montreal'
    else:
        print('Invalid bank.')
        return None

    account = input('Enter 8-character account number: ')

    if len(account) != 8:
        print('Account number must have 8 characters.')
        return None

    transit = input('Enter 3-digit transit number: ')

    if len(transit) != 3 or not transit.isascii() or not transit.isdigit():
        print('Transit number must have exactly 3 digits.')
        return None

    print('Direct Deposit information saved successfully!')

    return [bank, account, transit]


# MAIN PROGRAM

bank = select_bank()
print(f'Welcome to {bank}!')

if verify_pin():

    balance = 1000.00
    history = []
    deposit_info = None

    while True:

        print('\n--- ATM MENU ---')
        print('1 - Deposit')
        print('2 - Withdraw')
        print('3 - Check Balance')
        print('4 - Transaction History')
        print('5 - Direct Deposit')
        print('6 - Exit')

        option = input('Choose an option: ')

        if option == '1':
            balance = deposit(balance, history)

        elif option == '2':
            balance = withdraw(balance, history)

        elif option == '3':
            print(f'Balance: ${balance:.2f}')

        elif option == '4':
            if len(history) == 0:
                print('No transactions yet.')
            else:
                for transaction in history:
                    print(transaction)

        elif option == '5':
            info = direct_deposit()

            if info is not None:
                deposit_info = info

        elif option == '6':
            print('Thank you for banking with us!')
            break

        else:
            print('Invalid option.')