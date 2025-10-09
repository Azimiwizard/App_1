from main import parse_order_from_text, create_order_from_items, seed_database, app
import os
import sys
sys.path.append('.')


# Test parse_order_from_text

def test_parse_order():
    sample_text = "I want two burgers and one salad."
    items = parse_order_from_text(sample_text)
    print("Parsed items:", items)
    # Expected: [{'dish': 'Burger Deluxe', 'quantity': 2}, {'dish': 'Caesar Salad', 'quantity': 1}]

# Test create_order_from_items


def test_create_order():
    phone_number = "+1234567890"
    order_items = [{'dish': 'Burger Deluxe', 'quantity': 2},
                   {'dish': 'Caesar Salad', 'quantity': 1}]
    order = create_order_from_items(phone_number, order_items)
    print("Created order ID:", order.id, "Total:", order.total)


if __name__ == "__main__":
    with app.app_context():
        seed_database()
        test_parse_order()
        test_create_order()
