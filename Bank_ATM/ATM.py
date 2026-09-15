balance = 1000.00

print(f'Your current balance is: ${balance:.2f}')

print(
    '1 - Deposit\n'
    '2 - Withdraw\n'
    '3 - Check Balance\n'
    '4 - Exit\n'
)

while True:

    option = int(input('What would you like to do? '))

    if option == 1:
        deposit = float(input('How much would you like to deposit? '))
        if deposit <= 0:
            print('Cannot deposit zero or a negative amount')
        else:
            balance = balance + deposit
            print(f'Your new balance is: ${balance:.2f}')
    elif option == 2:
        withdraw = float(input('How much would you like to withdraw? '))
        if withdraw <= 0:
            print('Cannot withdraw zero or a negative amount')
        elif withdraw > balance:
            print('Insufficient Funds')
        else:
            balance = balance - withdraw
            print(f'Your new balance is: ${balance:.2f}')
    elif option == 3:
        print(f'Your current balance is: ${balance:.2f}')
    elif option == 4:
        print('Thank you for using the banking system.')
        break
    else:
        print('Invalid option. Please choose between 1 and 4.')