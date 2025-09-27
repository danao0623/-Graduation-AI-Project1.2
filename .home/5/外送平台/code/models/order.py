```python
import datetime

class Restaurant:
    def __init__(self, restaurantID, name, location):
        self.restaurantID = restaurantID
        self.name = name
        self.location = location

class DeliveryPerson:
    def __init__(self, deliveryPersonID, name, location):
        self.deliveryPersonID = deliveryPersonID
        self.name = name
        self.location = location

class Order:
    def __init__(self, orderID, status, estimatedDeliveryTime, restaurant, deliveryPerson):
        self.orderID = orderID
        self.status = status
        self.estimatedDeliveryTime = estimatedDeliveryTime
        self.restaurant = restaurant
        self.deliveryPerson = deliveryPerson

    def getOrderStatus(self):
        return self.status

    def setOrderStatus(self, status):
        self.status = status

# Example usage
restaurant1 = Restaurant("R123", "Restaurant A", "Location A")
deliveryPerson1 = DeliveryPerson("D456", "Delivery Person X", "Location X")
order1 = Order("O789", "Pending", datetime.datetime(2024, 3, 8, 18, 0, 0), restaurant1, deliveryPerson1)

print(order1.getOrderStatus())  # Output: Pending
order1.setOrderStatus("Processing")
print(order1.getOrderStatus())  # Output: Processing