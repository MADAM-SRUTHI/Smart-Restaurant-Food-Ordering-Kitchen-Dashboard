import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, MenuItem, Order, OrderItem
from .forms import OrderCreateForm


class RestaurantAppTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create staff user for kitchen dashboard
        self.staff_user = User.objects.create_user(
            username="chef_john",
            password="securepassword123",
            is_staff=True,
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username="regular_guest",
            password="guestpassword123",
            is_staff=False,
        )

        # Seed categories
        self.cat_appetizers = Category.objects.create(name="Appetizers", icon="bi-egg-fried")
        self.cat_main = Category.objects.create(name="Main Course", icon="bi-fire")
        self.cat_desserts = Category.objects.create(name="Desserts", icon="bi-cake2")
        self.cat_beverages = Category.objects.create(name="Beverages", icon="bi-cup-straw")

        # Seed menu items
        self.item_spring_rolls = MenuItem.objects.create(
            category=self.cat_appetizers,
            name="Veg Spring Rolls",
            description="Crispy golden vegetable spring rolls",
            price=Decimal("100.00"),
            is_vegetarian=True,
            is_available=True,
        )
        self.item_burger = MenuItem.objects.create(
            category=self.cat_main,
            name="Classic Veg Burger",
            description="Loaded veggie burger with cheese",
            price=Decimal("120.00"),
            is_vegetarian=True,
            is_available=True,
        )
        self.item_biryani = MenuItem.objects.create(
            category=self.cat_main,
            name="Hyderabadi Chicken Biryani",
            description="Fragrant dum biryani",
            price=Decimal("220.00"),
            is_vegetarian=False,
            is_available=True,
        )
        self.item_unavailable = MenuItem.objects.create(
            category=self.cat_beverages,
            name="Seasonal Special Shake",
            description="Currently out of season",
            price=Decimal("80.00"),
            is_vegetarian=True,
            is_available=False,
        )

    def test_homepage_renders_successfully(self):
        """Verify home page loads, displays categories and available items."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "restaurant_app/home.html")
        self.assertContains(response, "Smart Restaurant")
        self.assertContains(response, "Appetizers")
        self.assertContains(response, "Classic Veg Burger")
        self.assertContains(response, "Hyderabadi Chicken Biryani")
        # Unavailable item should not be rendered
        self.assertNotContains(response, "Seasonal Special Shake")

    def test_menu_item_properties(self):
        """Verify image property and dietary flags."""
        self.assertEqual(self.item_spring_rolls.static_image_name, "images/spring_rolls.jpg")
        self.assertEqual(self.item_burger.static_image_name, "images/burger.jpg")
        self.assertEqual(self.item_biryani.static_image_name, "images/biryani.jpg")
        self.assertTrue(self.item_spring_rolls.is_vegetarian)
        self.assertFalse(self.item_biryani.is_vegetarian)

    def test_order_form_validation(self):
        """Test OrderCreateForm validation."""
        valid_data = {
            "customer_name": "Rohan Sharma",
            "customer_phone": "9876543210",
            "table_number": "Table 3",
        }
        form = OrderCreateForm(data=valid_data)
        self.assertTrue(form.is_valid())

        invalid_data = {
            "customer_name": "R",  # too short
            "customer_phone": "123",  # invalid phone length
        }
        form_invalid = OrderCreateForm(data=invalid_data)
        self.assertFalse(form_invalid.is_valid())

    def test_place_order_success_and_server_calculation(self):
        """Verify order checkout, server-side tax and grand total calculation."""
        cart_payload = [
            {"id": self.item_spring_rolls.id, "quantity": 2},  # 2 * 100 = 200
            {"id": self.item_burger.id, "quantity": 1},        # 1 * 120 = 120
        ]
        # Subtotal: 320.00
        # Tax 5%: 16.00
        # Grand total: 336.00

        post_data = {
            "customer_name": "Anita Verma",
            "customer_phone": "9988776655",
            "table_number": "Table 8",
            "cart": json.dumps(cart_payload),
        }

        # Set session cart first to test clearing
        session = self.client.session
        session["cart"] = {"test": 1}
        session.save()

        response = self.client.post(reverse("place_order"), post_data)
        self.assertEqual(response.status_code, 302)

        # Verify Order in DB
        order = Order.objects.filter(customer_name="Anita Verma").first()
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_phone, "9988776655")
        self.assertEqual(order.table_number, "Table 8")
        self.assertEqual(order.status, "Received")
        self.assertEqual(order.total_amount, Decimal("336.00"))

        # Verify OrderItems
        items = order.items.all()
        self.assertEqual(items.count(), 2)

        # Check session cart was cleared
        self.assertNotIn("cart", self.client.session)

    def test_place_order_rejects_unavailable_item(self):
        """Order must fail if an unavailable menu item is in cart."""
        cart_payload = [
            {"id": self.item_unavailable.id, "quantity": 1},
        ]
        post_data = {
            "customer_name": "Sam",
            "customer_phone": "9876543210",
            "cart": json.dumps(cart_payload),
        }
        response = self.client.post(reverse("place_order"), post_data)
        self.assertEqual(response.status_code, 302)
        # Order should NOT have been created
        self.assertFalse(Order.objects.filter(customer_name="Sam").exists())

    def test_place_order_rejects_invalid_quantity(self):
        """Quantity < 1 or > 50 must be rejected."""
        cart_payload = [
            {"id": self.item_burger.id, "quantity": 999},
        ]
        post_data = {
            "customer_name": "Sam",
            "customer_phone": "9876543210",
            "cart": json.dumps(cart_payload),
        }
        response = self.client.post(reverse("place_order"), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Order.objects.filter(customer_name="Sam").exists())

    def test_track_order_view(self):
        """Test order tracking view by Order ID."""
        order = Order.objects.create(
            customer_name="Pooja Rao",
            customer_phone="9123456789",
            table_number="Table 1",
            total_amount=Decimal("150.00"),
            status="Preparing",
        )
        OrderItem.objects.create(
            order=order,
            menu_item=self.item_burger,
            quantity=1,
            price=Decimal("120.00"),
        )

        response = self.client.get(reverse("track_order_detail", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "restaurant_app/track_order.html")
        self.assertContains(response, f"Order #{order.id}")
        self.assertContains(response, "Preparing")
        self.assertEqual(order.status_step, 2)

    def test_order_status_api(self):
        """Test JSON status API endpoint."""
        order = Order.objects.create(
            customer_name="Arun Kumar",
            customer_phone="9876543210",
            total_amount=Decimal("100.00"),
            status="Ready",
        )
        response = self.client.get(reverse("order_status_api", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], order.id)
        self.assertEqual(data["status"], "Ready")
        self.assertEqual(data["status_step"], 3)

    def test_kitchen_dashboard_access_control(self):
        """Anonymous and regular users cannot access kitchen dashboard; staff can."""
        # Anonymous
        anon_resp = self.client.get(reverse("kitchen_dashboard"))
        self.assertEqual(anon_resp.status_code, 302)

        # Regular user
        self.client.force_login(self.regular_user)
        reg_resp = self.client.get(reverse("kitchen_dashboard"))
        self.assertEqual(reg_resp.status_code, 302)

        # Staff user
        self.client.force_login(self.staff_user)
        staff_resp = self.client.get(reverse("kitchen_dashboard"))
        self.assertEqual(staff_resp.status_code, 200)
        self.assertTemplateUsed(staff_resp, "restaurant_app/kitchen_dashboard.html")

    def test_kitchen_status_update_workflow(self):
        """Test advancing order status through Received -> Preparing -> Ready -> Completed."""
        order = Order.objects.create(
            customer_name="Kiran Patel",
            customer_phone="9876543210",
            total_amount=Decimal("100.00"),
            status="Received",
        )

        self.client.force_login(self.staff_user)

        # Transition 1: Received -> Preparing
        resp1 = self.client.post(
            reverse("update_order_status", kwargs={"order_id": order.id}),
            {"status": "Preparing"},
        )
        self.assertEqual(resp1.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "Preparing")

        # Transition 2: Preparing -> Ready
        resp2 = self.client.post(
            reverse("update_order_status", kwargs={"order_id": order.id}),
            {"status": "Ready"},
        )
        self.assertEqual(resp2.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "Ready")

        # Transition 3: Ready -> Completed
        resp3 = self.client.post(
            reverse("update_order_status", kwargs={"order_id": order.id}),
            {"status": "Completed"},
        )
        self.assertEqual(resp3.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "Completed")
