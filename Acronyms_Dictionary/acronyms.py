def find_acronym():

    look_up = input("What acronym would you like to look up?\n")

    found = False

    with open(r"C:\Users\spenc\Desktop\Python_for_IT_Automation\Acronyms_Dictionary\acronyms.txt") as file:

        for line in file:
            if look_up in line:
                print(line)
                found = True
                break
    if not found:
        print("The acronym does not exist")


def add_acronym():

    number_of_entry = int(input("How many acronyms do you want to add? "))

    for i in range(number_of_entry):
        acronym = input("Type in the acronym you want to add:\n")
        definition = input("What is the definition?:\n")
        with open(r"C:\Users\spenc\Desktop\Python_for_IT_Automation\Acronyms_Dictionary\acronyms.txt", "a") as file:
            file.write(acronym + " - " + definition + "\n")


def main():
    choice = input(
        "Do you want to find (F), add (A), or quit (Q)?\n"
    ).upper()
    while choice != "Q":
        if choice == "F":
            find_acronym()
        elif choice == "A":
            add_acronym()
        else:
            print("Invalid choice.")
        choice = input(
            "Do you want to find (F), add (A), or quit (Q)?\n"
        ).upper()
main()