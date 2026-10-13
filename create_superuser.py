import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurant_project.settings")
django.setup()

from django.contrib.auth.models import User
from decimal import Decimal


def create_or_update_superusers():
    # 1. Main superuser from environment or default
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@smartrestaurant.local")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123")

    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email, "is_staff": True, "is_superuser": True},
    )
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    if created:
        print(f"[create_superuser] Superuser '{username}' created successfully.")
    else:
        print(f"[create_superuser] Superuser '{username}' updated successfully.")

    # 2. Also ensure madamsruthi user exists for student/trainer access
    ms_user, ms_created = User.objects.get_or_create(
        username="madamsruthi",
        defaults={"email": "sruthi@smartrestaurant.local", "is_staff": True, "is_superuser": True},
    )
    ms_user.set_password(os.environ.get("STUDENT_PASSWORD", "admin123"))
    ms_user.is_staff = True
    ms_user.is_superuser = True
    ms_user.save()
    if ms_created:
        print("[create_superuser] User 'madamsruthi' created as staff/superuser.")


def seed_menu_data():
    from restaurant_app.models import Category, MenuItem

    categories_data = [
        {"name": "Appetizers", "icon": "bi-egg-fried"},
        {"name": "Main Course", "icon": "bi-fire"},
        {"name": "Desserts", "icon": "bi-cake2"},
        {"name": "Beverages", "icon": "bi-cup-straw"},
    ]

    cat_map = {}
    for cat_info in categories_data:
        cat_obj, _ = Category.objects.get_or_create(
            name=cat_info["name"],
            defaults={"icon": cat_info["icon"]},
        )
        cat_map[cat_obj.name] = cat_obj

    menu_items_data = [
        # Appetizers
        {
            "name": "Veg Spring Rolls",
            "category": "Appetizers",
            "price": Decimal("100.00"),
            "description": "Crispy golden rolls filled with seasoned fresh vegetables and sweet chili dip.",
            "is_vegetarian": True,
            "is_available": True,
            "image_url": "",
        },
        {
            "name": "Crispy Paneer Fingers",
            "category": "Appetizers",
            "price": Decimal("130.00"),
            "description": "Spiced cottage cheese strips batter-fried to golden perfection with mint chutney.",
            "is_vegetarian": True,
            "is_available": True,
            "image_url": "",
        },
        # Main Course
        {
            "name": "Classic Veg Burger",
            "category": "Main Course",
            "price": Decimal("120.00"),
            "description": "Juicy vegetable patty loaded with cheese slice, crispy lettuce, and signature sauce.",
            "is_vegetarian": True,
            "is_available": True,
            "image_url": "",
        },
        {
            "name": "Farmhouse Veg Pizza",
            "category": "Main Course",
            "price": Decimal("180.00"),
            "description": "Hand-tossed crust topped with mozzarella cheese, capsicum, olives, and mushrooms.",
            "is_vegetarian": True,
            "is_available": True,
            "image_url": "",
        },
        {
            "name": "Paneer Butter Masala",
            "category": "Main Course",
            "price": Decimal("160.00"),
            "description": "Succulent cottage cheese cubes simmered in a rich tomato, butter, and cashew gravy.",
            "is_vegetarian": True,
            "is_available": True,
            "image_url": "",
        },
        {
            "name": "Hyderabadi Chicken Biryani",
            "category": "Main Course",
            "price": Decimal("220.00"),
            "description": "Fragrant basmati rice dum cooked with tender chicken pieces, saffron, and aromatic spices.",
            "is_vegetarian": False,
            "is_available": True,
            "image_url": "",
        },
        # Desserts
        {
            "name": "Sizzling Chocolate Brownie",
            "category": "Desserts",
            "price": Decimal("90.00"),
            "description": "Warm fudgy chocolate brownie topped with chocolate syrup and vanilla ice cream scoop.",
            "is_vegetarian": True,
            "is_available": True,
            "image_url": "",
        },
        {
            "name": "Gulab Jamun with Ice Cream",
            "category": "Desserts",
            "price": Decimal("80.00"),
            "description": "Soft melt-in-the-mouth milk dumplings served warm with rich vanilla bean ice cream.",
            "is_vegetarian": True,
            "is_available": True,
            "image_url": "",
        },
        # Beverages
        {
            "name": "Masala Chai",
            "category": "Beverages",
            "price": Decimal("30.00"),
            "description": "Freshly brewed Indian tea infused with cardamom, ginger, and aromatic spices.",
            "is_vegetarian": True,
            "is_available": True,
            "image_url": "",
        },
        {
            "name": "Fresh Lime Soda",
            "category": "Beverages",
            "price": Decimal("50.00"),
            "description": "Refreshing sparkling soda with fresh squeezed lime juice, mint, and black salt.",
            "is_vegetarian": True,
            "is_available": True,
            "image_url": "",
        },
    ]

    for item_data in menu_items_data:
        cat = cat_map[item_data["category"]]
        # Find item by name
        item_obj = MenuItem.objects.filter(name__iexact=item_data["name"]).first()
        if not item_obj:
            # Also check if an older name existed (e.g. 'burger', 'pizza', 'masala chai')
            if "burger" in item_data["name"].lower():
                item_obj = MenuItem.objects.filter(name__icontains="burger").first()
            elif "pizza" in item_data["name"].lower():
                item_obj = MenuItem.objects.filter(name__icontains="pizza").first()
            elif "biryani" in item_data["name"].lower():
                item_obj = MenuItem.objects.filter(name__icontains="biryani").first()
            elif "chai" in item_data["name"].lower():
                item_obj = MenuItem.objects.filter(name__icontains="chai").first()
            elif "lime" in item_data["name"].lower() or "lemon" in item_data["name"].lower():
                item_obj = MenuItem.objects.filter(name__icontains="lemon").first() or MenuItem.objects.filter(name__icontains="lime").first()
            elif "brownie" in item_data["name"].lower():
                item_obj = MenuItem.objects.filter(name__icontains="brownie").first()
            elif "paneer" in item_data["name"].lower():
                item_obj = MenuItem.objects.filter(name__icontains="paneer").first()

        if item_obj:
            item_obj.name = item_data["name"]
            item_obj.category = cat
            item_obj.price = item_data["price"]
            item_obj.description = item_data["description"]
            item_obj.is_vegetarian = item_data["is_vegetarian"]
            item_obj.is_available = item_data["is_available"]
            item_obj.save()
        else:
            MenuItem.objects.create(
                category=cat,
                name=item_data["name"],
                price=item_data["price"],
                description=item_data["description"],
                is_vegetarian=item_data["is_vegetarian"],
                is_available=item_data["is_available"],
            )

    print(f"[seed_menu_data] Total MenuItems verified: {MenuItem.objects.count()}")


if __name__ == "__main__":
    create_or_update_superusers()
    seed_menu_data()
