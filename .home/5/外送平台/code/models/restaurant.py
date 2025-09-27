```python
from typing import List, Dict, Optional

class Restaurant:
    def __init__(self, restaurantId: int, name: str, rating: float, distance: float, photoUrl: str, menu: List[Dict]):
        self.restaurantId = restaurantId
        self.name = name
        self.rating = rating
        self.distance = distance
        self.photoUrl = photoUrl
        self.menu = menu

class Menu:
    def __init__(self, itemId: int, itemName: str, price: float, description: str):
        self.itemId = itemId
        self.itemName = itemName
        self.price = price
        self.description = description


# Example usage (replace with your actual database interaction)
restaurants = [
    Restaurant(1, "Restaurant A", 4.5, 1.2, "url1", [Menu(1, "Dish A", 10.0, "Description A"), Menu(2, "Dish B", 12.0, "Description B")]),
    Restaurant(2, "Restaurant B", 3.8, 2.5, "url2", [Menu(3, "Dish C", 8.0, "Description C")]),
]

def get_restaurant_by_id(restaurantId: int) -> Optional[Restaurant]:
    for restaurant in restaurants:
        if restaurant.restaurantId == restaurantId:
            return restaurant
    return None

def get_all_restaurants() -> List[Restaurant]:
    return restaurants

# ... (Add other functions for database interactions like insert, update, delete, etc.)

```python
class Restaurant:
    def __init__(self, restaurantID, name, address):
        self.restaurantID = restaurantID
        self.name = name
        self.address = address

    def getRestaurantInfo(self):
        return f"Restaurant ID: {self.restaurantID}, Name: {self.name}, Address: {self.address}"

# Example usage (replace with your actual data access methods)
restaurant1 = Restaurant("R123", "The Italian Place", "123 Main St")
restaurant_info = restaurant1.getRestaurantInfo()
print(restaurant_info)

restaurant2 = Restaurant("R456", "Burger Bliss", "456 Oak Ave")
restaurant_info = restaurant2.getRestaurantInfo()
print(restaurant_info)