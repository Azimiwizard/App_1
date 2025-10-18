import requests

# Test adding a dish as admin
session = requests.Session()

# First login
login_response = session.post('http://127.0.0.1:5000/login', data={
    'email': 'test30@example.com',
    'password': 'password123'
})
print('Login Status:', login_response.status_code)

# Then try to add a dish
add_dish_response = session.post('http://127.0.0.1:5000/admin/dish/add', data={
    'name': 'Test Dish',
    'price': '10.99',
    'description': 'Test description',
    'section': 'Breakfast'
})
print('Add Dish Status:', add_dish_response.status_code)

if add_dish_response.status_code == 500:
    print('Internal Server Error - Full Response:')
    print(add_dish_response.text)
else:
    print('Success - Response contains success:',
          'success' in add_dish_response.text.lower())
    print('Response contains dish added:',
          'dish added' in add_dish_response.text.lower())
