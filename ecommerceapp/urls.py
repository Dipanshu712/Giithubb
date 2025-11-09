from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),

    path('contact/', views.contact, name="contact"),
    path('about/', views.about, name="about"),

    path('product/<int:product_id>/', views.product_detail, name="product_detail"),

    path('add-to-cart/', views.add_to_cart, name="add_to_cart"),

    path('Shop_cart/', views.Shop_cart, name="Shop_cart"),
    path('Shop_checkout/', views.checkout, name="Shop_checkout"),
    path('Shop_order_complete/', views.Shop_order_complete, name="Shop_order_complete"),

    path('paymenthandler/', views.paymenthandler, name="paymenthandler"),

    path('my-account/', views.account_dashboard, name="account_dashboard"),
    path('my-orders/', views.account_orders, name="account_orders"),
]
