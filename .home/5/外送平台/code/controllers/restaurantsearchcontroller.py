```python
class RestaurantSearchController:
    def __init__(self):
        self.currentLocation = None
        self.restaurants = []
        self.filteredRestaurants = []

    def filterRestaurants(self, criteria):
        self.filteredRestaurants = [restaurant for restaurant in self.restaurants if self.matchesCriteria(restaurant, criteria)]
        return self.filteredRestaurants

    def matchesCriteria(self, restaurant, criteria):
        # Implement your criteria matching logic here
        # This is a placeholder, replace with actual logic
        return True

    def getRestaurantMenu(self, restaurantId):
        # Implement your menu retrieval logic here
        # This is a placeholder, replace with actual logic
        return []