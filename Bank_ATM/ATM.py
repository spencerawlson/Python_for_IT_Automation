pin = int(input('Please choose a PIN:\n'))

attempt = 0
trans_his = []

while attempt < 3:
    pin_customer = int(input('Enter your PIN:\n'))
    if pin_customer == pin:
        print('PIN accepted!')
        break
    else:
        attempt = attempt + 1
        print('Incorrect PIN')
        if attempt < 3:
            print(f'You have {3 - attempt} attempts remaining.')
if attempt == 3:
    print('Account BLOCKED. Too many incorrect PIN attempts.')
else:
    balance = 1000.00

    print(f'Your current balance is: ${balance:.2f}')

    print(
        '1 - Deposit\n'
        '2 - Withdraw\n'
        '3 - Check Balance\n'
        '4 - View Transaction History\n'
        '5 - Exit\n'
    )

    while True:

        option = int(input('What would you like to do? '))

        if option == 1:
            deposit = float(input('How much would you like to deposit? '))
            if deposit <= 0:
                print('Cannot deposit zero or a negative amount')
            else:
                balance = balance + deposit
                trans_his.append(f'Deposited ${deposit:.2f}')
                print(f'Your new balance is: ${balance:.2f}')
        elif option == 2:
            withdraw = float(input('How much would you like to withdraw? '))
            if withdraw <= 0:
                print('Cannot withdraw zero or a negative amount')
            elif withdraw > balance:
                print('Insufficient Funds')
            else:
                balance = balance - withdraw
                trans_his.append(f'Withdrew ${withdraw:.2f}')
                print(f'Your new balance is: ${balance:.2f}')
        elif option == 3:
            print(f'Your current balance is: ${balance:.2f}')
        elif option == 4:
            print('\n--- Transaction History ---')
            if len(trans_his) == 0:
                print('No transactions yet.')
            else:
                for transaction in trans_his:
                    print(transaction)
        elif option == 5:
            print('Thank you for using the banking system.')
            break
        else:
            print('Invalid option. Please choose between 1 and 4.')