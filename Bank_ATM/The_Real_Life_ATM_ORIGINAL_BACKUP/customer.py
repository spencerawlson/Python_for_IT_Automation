class Customer:
    
    def __init__(self, customer_id, name, pin):
        self.customer_id = customer_id
        self.name = name
        self.pin = pin

    def verify_pin(self, entered_pin):
        return self.pin == str(entered_pin)