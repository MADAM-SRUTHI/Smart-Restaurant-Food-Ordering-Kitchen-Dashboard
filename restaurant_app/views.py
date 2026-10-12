from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
import json
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import MenuItem, Order, OrderItem


def home(request):
    items = MenuItem.objects.filter(
        is_available=True
    ).select_related("category")

    return render(
        request,
        "restaurant_app/home.html",
        {"items": items}
    )


@require_POST
def place_order(request):
    try:
        cart = json.loads(request.POST.get("cart", "[]"))

        customer_name = request.POST.get(
            "customer_name", ""
        ).strip()

        customer_phone = request.POST.get(
            "customer_phone", ""
        ).strip()

        table_number = request.POST.get(
            "table_number", ""
        ).strip()

        if not customer_name or not customer_phone or not cart:
            messages.error(
                request,
                "Please enter your details and add food to your cart."
            )
            return redirect("home")

        if not isinstance(cart, list):
            raise ValueError("Invalid cart")

        total = Decimal("0.00")
        order_items = []
        seen_ids = set()

        for item in cart:
            item_id = int(item["id"])
            quantity = int(item["quantity"])

            if item_id in seen_ids:
                raise ValueError("Duplicate cart item")

            seen_ids.add(item_id)

            if quantity < 1 or quantity > 50:
                raise ValueError("Invalid quantity")

            menu_item = MenuItem.objects.get(
                id=item_id,
                is_available=True
            )

            total += menu_item.price * quantity
            order_items.append((menu_item, quantity))

        tax = (total * Decimal("0.05")).quantize(
            Decimal("0.01")
        )
        grand_total = total + tax

        with transaction.atomic():
            order = Order.objects.create(
                customer_name=customer_name,
                customer_phone=customer_phone,
                table_number=table_number,
                total_amount=grand_total,
            )

            for menu_item, quantity in order_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    price=menu_item.price,
                )

        return render(
            request,
            "restaurant_app/order_success.html",
            {"order": order}
        )

    except (
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        MenuItem.DoesNotExist,
    ):
        messages.error(
            request,
            "Invalid cart. Please clear the cart and try again."
        )
        return redirect("home")
@staff_member_required
def kitchen_dashboard(request):
    orders = Order.objects.prefetch_related(
        "items__menu_item"
    ).order_by("-created_at")

    context = {
        "orders": orders,
        "total_orders": Order.objects.count(),
        "pending_orders": Order.objects.filter(
            status__in=["Received", "Preparing"]
        ).count(),
        "ready_orders": Order.objects.filter(
            status="Ready"
        ).count(),
        "completed_orders": Order.objects.filter(
            status="Completed"
        ).count(),
    }

    return render(
        request,
        "restaurant_app/kitchen_dashboard.html",
        context
    )


@staff_member_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    allowed_statuses = [
        "Received", "Preparing", "Ready", "Completed"
    ]
    new_status = request.POST.get("status", "")

    if new_status not in allowed_statuses:
        messages.error(request, "Invalid order status.")
    else:
        order.status = new_status
        order.save(update_fields=["status"])
        messages.success(
            request,
            f"Order #{order.id} status updated to {new_status}."
        )

    return redirect("kitchen_dashboard")
