import requests

session = requests.Session()

# Login
login_response = session.post('http://127.0.0.1:5000/login', data={
    'email': 'test30@example.com',
    'password': 'password123'
})
print('Login Status:', login_response.status_code)

# Add dish
add_dish_response = session.post('http://127.0.0.1:5000/admin/dish/add', data={
    'name': 'Test Dish',
    'price': '10.99',
    'description': 'Test description',
    'section': 'Breakfast'
})
print('Add Dish Status:', add_dish_response.status_code)

if add_dish_response.status_code == 500:
    print('Internal Server Error')
else:
    print('Success - Response contains dish added:',
          'dish added' in add_dish_response.text.lower())
