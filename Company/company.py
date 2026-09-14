from Company.employee import Employee
from typing import List

class Company:
    def __init__(self):
        self.employee: List[Employee]= []

    def add_employee(self, employee:Employee):
        self.employee.append(employee)

    def display_employees(self):
        for employee in self.employee:
                print(f"Paycheck for: {employee.fname} {employee.lname}")
                print(f"Amount: ${employee.calculate_paycheck():,.2f}")

def main():    
    company = Company()
    employee1 = Employee("John", "Doe", 50000)
    company.add_employee(employee1)
    employee2 = Employee("Jane", "Smith", 60000)
    company.add_employee(employee2)
    employee3 = Employee("Bob", "Johnson", 55000)
    company.add_employee(employee3)
    company.display_employees()

main()