class Employee:
    def __init__(self, name, age, position, salary):
        self.__dict__["name"] = name
        self.__dict__["age"] = age
        self.__dict__["position"] = position
        self.__dict__["salary"] = salary

number_emp = input("Please enter the number of employees you want to add: " )
employees = []

def main():
    for e in number_emp:
        name = input("Please enter the employee's name: ")
        age = int(input("Please enter the employee's age: "))
        position = input("Please enter the employee's position: ")
        salary = float(input("Please enter the employee's salary: "))

        emp = Employee(name, age, position, salary)
        employees.append(emp)

    for emp in employees:
        print(f"{emp.name} is currently {emp.age} and a {emp.position} with a salary of {emp.salary  }")

main()
