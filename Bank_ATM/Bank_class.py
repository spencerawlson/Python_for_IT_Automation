
class Bank:

    def __init__(self, name):

        self.name = name
        self.balance = 1000.00
        self.pin = None
        self.trans_his = []
        self.direct_deposit_info = {}

    # CREATE PIN AND VERIFY CUSTOMER
    def account(self):

        self.pin = int(input('Please choose a PIN:\n'))

        attempt = 0

        while attempt < 3:

            pin_customer = int(input('Enter your PIN:\n'))

            if pin_customer == self.pin:

                print('PIN accepted!')
                return True

            else:

                attempt += 1
                print('Incorrect PIN')

                if attempt < 3:

                    print(
                        f'You have {3 - attempt} attempts remaining.'
                    )

        print('Account BLOCKED. Too many incorrect PIN attempts.')

        return False

    # DEPOSIT
    def deposit(self):

        deposit = float(input('How much would you like to deposit? '))

        if deposit <= 0:

            print('Cannot deposit zero or a negative amount')

        else:

            self.balance += deposit

            self.trans_his.append(
                f'Deposited ${deposit:.2f}'
            )

            print(f'Your new balance is: ${self.balance:.2f}')

    # WITHDRAW
    def withdraw(self):

        withdraw = float(input('How much would you like to withdraw? '))

        if withdraw <= 0:

            print('Cannot withdraw zero or a negative amount')

        elif withdraw > self.balance:

            print('Insufficient Funds')

        else:

            self.balance -= withdraw

            self.trans_his.append(
                f'Withdrew ${withdraw:.2f}'
            )

            print(f'Your new balance is: ${self.balance:.2f}')

    # CHECK BALANCE
    def check_balance(self):

        print(f'Your current balance is: ${self.balance:.2f}')

    # TRANSACTION HISTORY
    def view_transactions(self):

        print('\n--- Transaction History ---')

        if len(self.trans_his) == 0:

            print('No transactions yet.')

        else:

            for transaction in self.trans_his:

                print(transaction)

    # DIRECT DEPOSIT
    def direct_deposit(self):

        print('\n--- Direct Deposit Setup ---')

        print(
            'Available Banks:\n'
            '1 - CIBC\n'
            '2 - RBC\n'
            '3 - Bank of Montreal\n'
        )

        bank = input('Please select a bank (1, 2, or 3): ')

        if bank == '1':

            bank_name = 'CIBC'

        elif bank == '2':

            bank_name = 'RBC'

        elif bank == '3':

            bank_name = 'Bank of Montreal'

        else:

            print('Error: Invalid bank selected.')
            return

        account_number = input(
            'Enter your 8-character account number: '
        )

        if len(account_number) != 8:

            print(
                'Error: Account number must contain exactly 8 characters.'
            )
            return

        transit_number = input(
            'Enter your 3-digit transit number: '
        )

        if (
            len(transit_number) != 3
            or not transit_number.isascii()
            or not transit_number.isdigit()
        ):

            print(
                'Error: Transit number must contain exactly 3 digits.'
            )
            return

        # Save only when all information is valid
        self.direct_deposit_info = {
            'bank': bank_name,
            'account_number': account_number,
            'transit_number': transit_number
        }

        print(
            '\nDirect Deposit information has been saved successfully!'
        )

    # ATM MENU
    def menu(self):

        print(f'Your current balance is: ${self.balance:.2f}')

        while True:

            print(
                '\n--- ATM MENU ---\n'
                '1 - Deposit\n'
                '2 - Withdraw\n'
                '3 - Check Balance\n'
                '4 - View Transaction History\n'
                '5 - Direct Deposit\n'
                '6 - Exit\n'
            )

            option = input('What would you like to do? ')

            if option == '1':

                self.deposit()

            elif option == '2':

                self.withdraw()

            elif option == '3':

                self.check_balance()

            elif option == '4':

                self.view_transactions()

            elif option == '5':

                self.direct_deposit()

            elif option == '6':

                print('Thank you for using the banking system.')
                break

            else:

                print('Invalid option. Please choose between 1 and 6.')


# MAIN PROGRAM

print('Welcome to the ATM Banking System!')

# BANK SELECTION
print(
    '\nPlease select your bank:\n'
    '1 - CIBC\n'
    '2 - RBC\n'
    '3 - Bank of Montreal\n'
)

while True:

    bank_choice = input('Enter your bank selection (1, 2, or 3): ')

    if bank_choice == '1':

        bank_name = 'CIBC'
        break

    elif bank_choice == '2':

        bank_name = 'RBC'
        break

    elif bank_choice == '3':

        bank_name = 'Bank of Montreal'
        break

    else:

        print('Invalid bank. Please select one of the three banks.')


# CREATE BANK OBJECT
my_bank = Bank(bank_name)

print(f'\nWelcome to {my_bank.name}!')

# AUTHENTICATE AND START ATM
if my_bank.account():

    my_bank.menu()