
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("place-order/", views.place_order, name="place_order"),
    path("kitchen/", views.kitchen_dashboard, name="kitchen_dashboard"),
    path(
        "kitchen/order/<int:order_id>/status/",
        views.update_order_status,
        name="update_order_status",
    ),
]
