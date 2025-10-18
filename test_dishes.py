from db import get_all_dishes

dishes = get_all_dishes()
print(f"Total dishes: {len(dishes)}")

for dish in dishes[:5]:  # Show first 5 dishes
    print(f"- {dish['name']}: ${dish['price']} ({dish['section']})")
