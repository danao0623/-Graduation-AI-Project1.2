```python
class MenuItem:
    def __init__(self, menuId, menuName, price, image, description):
        self.menuId = menuId
        self.menuName = menuName
        self.price = price
        self.image = image
        self.description = description

    def setMenuName(self, name):
        self.menuName = name

    def setPrice(self, price):
        self.price = price

    def setImage(self, image):
        self.image = image

    def setDescription(self, description):
        self.description = description

# Example usage (replace with your actual database interaction)
menu_item = MenuItem(1, "Pizza", 15.99, "pizza.jpg", "Delicious pizza")
print(menu_item.menuName)  # Output: Pizza
menu_item.setMenuName("Pepperoni Pizza")
print(menu_item.menuName)  # Output: Pepperoni Pizza

# Placeholder for database interaction (replace with your actual database library)
def insert_menu_item(menu_item):
    # Code to insert menu_item into the database
    pass

def update_menu_item(menu_item):
    # Code to update menu_item in the database
    pass

def delete_menu_item(menu_id):
    # Code to delete menu_item from the database
    pass

def select_menu_item(menu_id):
    # Code to select menu_item from the database
    pass