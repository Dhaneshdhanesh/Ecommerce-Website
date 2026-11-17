from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path(
        'add-to-cart/<int:id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'cart/',
        views.cart,
        name='cart'
    ),

    path(
        'update-cart/<int:id>/',
        views.update_cart,
        name='update_cart'
    ),

    path(
        'remove-cart/<int:id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    path(
        'my-orders/',
        views.myorders,
        name='myorders'
    ),

    path(
        'cancel-order/<int:id>/',
        views.cancel_order,
        name='cancel_order'
    ),

]