class Employee:
    def __init__(self, fname : str, lname : str, salary : float):
        self.fname = fname
        self.lname = lname
        self.salary = salary

    def calculate_paycheck(self):
        return self.salary / 52
