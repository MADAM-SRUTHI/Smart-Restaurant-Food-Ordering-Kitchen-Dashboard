import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import OrderCreateForm, OrderStatusUpdateForm
from .models import Category, MenuItem, Order, OrderItem


def home(request):
    """
    Renders the responsive restaurant food menu grouped by categories,
    with dietary badges, price cards, and interactive shopping cart.
    """
    categories = Category.objects.prefetch_related(
        "items"
    ).all().order_by("name")

    items = MenuItem.objects.filter(
        is_available=True
    ).select_related("category").order_by("category__name", "name")

    form = OrderCreateForm()

    # Pass session cart item count if any
    session_cart = request.session.get("cart", {})
    cart_count = sum(item.get("quantity", 0) for item in session_cart.values()) if isinstance(session_cart, dict) else 0

    return render(
        request,
        "restaurant_app/home.html",
        {
            "categories": categories,
            "items": items,
            "form": form,
            "cart_count": cart_count,
        },
    )


@require_POST
def place_order(request):
    """
    Validates customer input and shopping cart contents.
    Performs server-side price recalculation, ensures availability,
    records the Order and OrderItems atomically, and clears the session cart.
    """
    form = OrderCreateForm(request.POST)

    if not form.is_valid():
        error_msg = " ".join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()])
        messages.error(request, f"Please correct the errors in the form: {error_msg}")
        return redirect("home")

    raw_cart = request.POST.get("cart", "[]")
    try:
        cart = json.loads(raw_cart)
    except (json.JSONDecodeError, TypeError):
        messages.error(request, "Invalid cart data. Please add items and try again.")
        return redirect("home")

    if not cart or not isinstance(cart, list):
        messages.error(request, "Your cart is empty. Please select food items before placing an order.")
        return redirect("home")

    # Server-side validation of cart items and quantities
    order_items_data = []
    subtotal = Decimal("0.00")
    seen_ids = set()

    try:
        for entry in cart:
            item_id = int(entry.get("id"))
            quantity = int(entry.get("quantity", 1))

            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)

            if quantity < 1 or quantity > 50:
                messages.error(request, f"Invalid quantity for item #{item_id}.")
                return redirect("home")

            # Verify against database for availability and true current price
            menu_item = MenuItem.objects.get(id=item_id, is_available=True)
            item_subtotal = menu_item.price * quantity
            subtotal += item_subtotal
            order_items_data.append((menu_item, quantity, menu_item.price))

    except (MenuItem.DoesNotExist, ValueError, KeyError):
        messages.error(request, "One or more items in your cart are invalid or currently unavailable.")
        return redirect("home")

    if not order_items_data:
        messages.error(request, "No valid items found in your order.")
        return redirect("home")

    # 5% Tax calculation (Server-side enforced)
    tax = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
    grand_total = subtotal + tax

    # Save order and order items in database atomically
    with transaction.atomic():
        order = form.save(commit=False)
        order.total_amount = grand_total
        order.status = "Received"
        order.save()

        for menu_item, quantity, price in order_items_data:
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=price,
            )

    # Clear Django session cart after successful checkout
    if "cart" in request.session:
        del request.session["cart"]
        request.session.modified = True

    return redirect("order_success", order_id=order.id)


def order_success(request, order_id):
    """
    Displays order confirmation screen with Order ID, customer details,
    and a direct link to track order progress.
    """
    order = get_object_or_404(
        Order.objects.prefetch_related("items__menu_item"),
        id=order_id
    )
    return render(
        request,
        "restaurant_app/order_success.html",
        {"order": order}
    )


def track_order(request, order_id=None):
    """
    Order tracking page by Order ID.
    Supports looking up an order either via URL parameter (/track/12/)
    or through a search query (/track/?order_id=12).
    """
    order = None
    query_id = order_id or request.GET.get("order_id", "").strip()

    if query_id:
        try:
            lookup_id = int(query_id)
            order = Order.objects.filter(id=lookup_id).prefetch_related(
                "items__menu_item"
            ).first()
            if not order:
                messages.warning(request, f"Order #{lookup_id} not found. Please verify your Order ID.")
        except ValueError:
            messages.warning(request, "Invalid Order ID entered. Please enter a valid numeric ID.")

    return render(
        request,
        "restaurant_app/track_order.html",
        {
            "order": order,
            "query_id": query_id,
        },
    )


@require_GET
def order_status_api(request, order_id):
    """
    JSON API endpoint returning live order status and step for real-time polling.
    """
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return JsonResponse({"error": "Order not found"}, status=404)

    return JsonResponse({
        "id": order.id,
        "status": order.status,
        "status_step": order.status_step,
        "status_badge_class": order.status_badge_class,
        "elapsed_minutes": order.elapsed_minutes,
        "total_amount": str(order.total_amount),
    })


@staff_member_required
def kitchen_dashboard(request):
    """
    Kitchen dashboard showing Received -> Preparing -> Ready -> Completed.
    Enables staff to view active orders and advance order statuses.
    """
    status_filter = request.GET.get("status", "").strip()

    orders_qs = Order.objects.prefetch_related("items__menu_item")

    if status_filter in ["Received", "Preparing", "Ready", "Completed"]:
        orders = orders_qs.filter(status=status_filter).order_by("created_at")
    else:
        # Prioritize active orders (Received first, then Preparing, Ready, Completed)
        orders = orders_qs.order_by("-created_at")

    total_orders = Order.objects.count()
    received_count = Order.objects.filter(status="Received").count()
    preparing_count = Order.objects.filter(status="Preparing").count()
    ready_count = Order.objects.filter(status="Ready").count()
    completed_count = Order.objects.filter(status="Completed").count()

    context = {
        "orders": orders,
        "total_orders": total_orders,
        "received_count": received_count,
        "preparing_count": preparing_count,
        "ready_count": ready_count,
        "completed_count": completed_count,
        "active_filter": status_filter,
        "status_choices": [s[0] for s in Order.STATUS_CHOICES],
    }

    return render(
        request,
        "restaurant_app/kitchen_dashboard.html",
        context
    )


@staff_member_required
@require_POST
def update_order_status(request, order_id):
    """
    Updates the status of an order (Received -> Preparing -> Ready -> Completed).
    Supports both traditional POST redirect and asynchronous fetch requests.
    """
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get("status", "").strip()

    allowed_statuses = [s[0] for s in Order.STATUS_CHOICES]

    if new_status not in allowed_statuses:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": "Invalid status"}, status=400)
        messages.error(request, "Invalid order status requested.")
    else:
        order.status = new_status
        order.save(update_fields=["status"])
        msg = f"Order #{order.id} status updated to {new_status}."

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "order_id": order.id,
                "status": order.status,
                "message": msg,
            })

        messages.success(request, msg)

    # Redirect back preserving current filter if present
    redirect_filter = request.POST.get("current_filter", "")
    if redirect_filter:
        return redirect(f"/kitchen/?status={redirect_filter}")
    return redirect("kitchen_dashboard")
