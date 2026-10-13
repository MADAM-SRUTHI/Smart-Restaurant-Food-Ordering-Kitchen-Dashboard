from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="items"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_vegetarian = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ["category__name", "name"]

    def __str__(self):
        return self.name

    @property
    def static_image_name(self):
        """Map item to known static images if image_url is not set."""
        name_l = self.name.lower()
        if "spring" in name_l or "roll" in name_l:
            return "images/spring_rolls.jpg"
        if "burger" in name_l:
            return "images/burger.jpg"
        if "pizza" in name_l:
            return "images/pizza.jpg"
        if "biryani" in name_l:
            return "images/biryani.jpg"
        if "brownie" in name_l:
            return "images/chocolate_brownie.jpg"
        if "paneer" in name_l or "panner" in name_l:
            return "images/paneer.jpg"
        if "chai" in name_l or "tea" in name_l:
            return "images/masala_chai.jpg"
        if "lime" in name_l or "lemon" in name_l or "soda" in name_l:
            return "images/lime_soda.jpg"
        return ""


class Order(models.Model):
    STATUS_CHOICES = [
        ("Received", "Received"),
        ("Preparing", "Preparing"),
        ("Ready", "Ready"),
        ("Completed", "Completed"),
    ]

    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    table_number = models.CharField(max_length=20, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Received"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.customer_name}"

    @property
    def status_step(self):
        mapping = {
            "Received": 1,
            "Preparing": 2,
            "Ready": 3,
            "Completed": 4,
        }
        return mapping.get(self.status, 1)

    @property
    def status_badge_class(self):
        mapping = {
            "Received": "bg-primary",
            "Preparing": "bg-warning text-dark",
            "Ready": "bg-info text-dark",
            "Completed": "bg-success",
        }
        return mapping.get(self.status, "bg-secondary")

    @property
    def elapsed_minutes(self):
        delta = timezone.now() - self.created_at
        return max(0, int(delta.total_seconds() // 60))


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.price
