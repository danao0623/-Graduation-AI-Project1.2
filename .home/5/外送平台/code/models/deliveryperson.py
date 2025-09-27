```python
class DeliveryPerson:
    def __init__(self, deliveryPersonID, name, phone):
        self.deliveryPersonID = deliveryPersonID
        self.name = name
        self.phone = phone

    def getDeliveryPersonInfo(self):
        return f"ID: {self.deliveryPersonID}, Name: {self.name}, Phone: {self.phone}"