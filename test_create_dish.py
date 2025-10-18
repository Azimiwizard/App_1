from db import create_dish

# Test data from the failing request
dish_data = {
    'name': 'Test Dish',
    'price': 10.99,  # float
    'description': 'Test description',
    'section': 'Breakfast'
}

print("Testing create_dish with data:", dish_data)
result = create_dish(**dish_data)
print("Result:", result)
