from django.urls import path
from . import views

urlpatterns = [

    path('', views.register, name='index'),

    path('register/', views.register, name='register'),

    path('login/', views.user_login, name='login'),

    path('logout/', views.user_logout, name='logout'),

    path(
        'seller/dashboard/',
        views.seller_dashboard,
        name='seller_dashboard'
    ),

    path(
        'seller/add-product/',
        views.add_product,
        name='add_product'
    ),

    path(
        'seller/my-products/',
        views.myproducts,
        name='myproducts'
    ),

    path(
        'seller/edit-product/<int:id>/',
        views.edit_product,
        name='edit_product'
    ),

    path(
        'seller/delete-product/<int:id>/',
        views.delete_product,
        name='delete_product'
    ),

    path(
        'seller/manage-orders/',
        views.manage_orders,
        name='manage_orders'
    ),

    path(
        'seller/update-order/<int:id>/',
        views.update_order_status,
        name='update_order_status'
    ),

]