```python
class Dish:
    def __init__(self, dishId, menuId, name, price, imageUrl, description):
        self.dishId = dishId
        self.menuId = menuId
        self.name = name
        self.price = price
        self.imageUrl = imageUrl
        self.description = description

    def __eq__(self, other):
        return (self.dishId, self.menuId, self.name, self.price, self.imageUrl, self.description) == \
               (other.dishId, other.menuId, other.name, other.price, other.imageUrl, other.description)

    def __hash__(self):
        return hash((self.dishId, self.menuId, self.name, self.price, self.imageUrl, self.description))


# Example usage (replace with your actual database interaction logic)
dish1 = Dish(1, 101, "Spaghetti Carbonara", 15.99, "url1", "Classic Italian dish")
dish2 = Dish(2, 101, "Spaghetti Carbonara", 15.99, "url1", "Classic Italian dish") #duplicate object
dish3 = Dish(3, 102, "Margherita Pizza", 12.50, "url2", "Simple yet delicious")

dishes = [dish1, dish2, dish3]

# Simulate database operations (replace with your actual database interaction)
def insert_dish(dish):
    print(f"Inserting dish: {dish.name}")
    # Add database insertion logic here

def update_dish(dish):
    print(f"Updating dish: {dish.name}")
    # Add database update logic here

def delete_dish(dish):
    print(f"Deleting dish: {dish.name}")
    # Add database delete logic here

def select_dish(dish_id):
    print(f"Selecting dish with ID: {dish_id}")
    # Add database selection logic here
    for dish in dishes:
        if dish.dishId == dish_id:
            return dish
    return None

for dish in dishes:
    insert_dish(dish)

updated_dish = Dish(1, 101, "Spaghetti Carbonara with extra cheese", 17.99, "url1", "Classic Italian dish with extra cheese")
update_dish(updated_dish)

delete_dish(dish2)

selected_dish = select_dish(3)
print(f"Selected dish: {selected_dish.name}")