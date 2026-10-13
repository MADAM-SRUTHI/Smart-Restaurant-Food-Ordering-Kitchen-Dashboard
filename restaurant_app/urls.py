from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("place-order/", views.place_order, name="place_order"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    path("track/", views.track_order, name="track_order"),
    path("track/<int:order_id>/", views.track_order, name="track_order_detail"),
    path("api/order/<int:order_id>/status/", views.order_status_api, name="order_status_api"),
    path("kitchen/", views.kitchen_dashboard, name="kitchen_dashboard"),
    path(
        "kitchen/order/<int:order_id>/status/",
        views.update_order_status,
        name="update_order_status",
    ),
]
