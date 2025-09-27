```python
class Menu:
    def __init__(self, menuId, restaurantId, dishes):
        self.menuId = menuId
        self.restaurantId = restaurantId
        self.dishes = dishes

class Dish:
    def __init__(self, dishId, dishName, price):
        self.dishId = dishId
        self.dishName = dishName
        self.price = price

# Example usage (replace with your actual data fetching and processing logic)
menu1 = Menu(1, 101, [Dish(1, "Dish A", 10.99), Dish(2, "Dish B", 15.99)])
menu2 = Menu(2, 102, [Dish(3, "Dish C", 8.99), Dish(4, "Dish D", 12.99)])

menus = [menu1, menu2]

def get_menu_by_restaurant_id(restaurant_id):
    result = [menu for menu in menus if menu.restaurantId == restaurant_id]
    return result

def add_menu(menu):
    menus.append(menu)

def update_menu(menu_id, updated_menu):
    for i, menu in enumerate(menus):
        if menu.menuId == menu_id:
            menus[i] = updated_menu
            return
    raise ValueError("Menu not found")

def delete_menu(menu_id):
    for i, menu in enumerate(menus):
        if menu.menuId == menu_id:
            del menus[i]
            return
    raise ValueError("Menu not found")

# Example usage of functions
print(get_menu_by_restaurant_id(101))
add_menu(Menu(3, 103, [Dish(5, "Dish E", 11.99)]))
print(menus)
update_menu(1, Menu(1, 101, [Dish(1, "Dish A Updated", 11.99), Dish(2, "Dish B", 15.99)]))
print(menus)
delete_menu(2)
print(menus)