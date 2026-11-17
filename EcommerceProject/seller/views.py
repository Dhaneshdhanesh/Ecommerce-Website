from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction

from .models import User, Product
from .forms import RegisterForm, ProductForm
from .decorators import role_required


from buyer.models import Order






# 1. SINGLE REGISTRATION

def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            role = form.cleaned_data['role']

            # Only one seller allowed
            if role == 'SELLER' and User.objects.filter(
                role='SELLER'
            ).exists():

                messages.error(
                    request,
                    'Seller account already exists!'
                )

            else:

                user = form.save()

                messages.success(
                    request,
                    'Registration successful! Please login.'
                )

                return redirect('login')

    else:

        form = RegisterForm()

    return render(request,  'seller/register.html', {'form': form})


# 2. COMMON LOGIN

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.role == 'SELLER':

                return redirect('seller_dashboard')

            elif user.role == 'BUYER':

                return redirect('home')

        else:

            messages.error(
                request,
                'Invalid username or password'
            )

    return render(request, 'seller/login.html')


# 3. LOGOUT

def user_logout(request):

    if request.method == 'POST':

        logout(request)

        return redirect('login')

    return redirect('login')


# 4. SELLER DASHBOARD

@role_required('SELLER')
def seller_dashboard(request):

    products = Product.objects.all()

    orders = Order.objects.exclude(
        status='CANCELLED'
    )

    context = {
        'products': products,
        'orders': orders,
        'total_products': products.count(),
        'total_orders': orders.count(),
    }

    return render(
        request,
        'seller/dashboard.html',
        context
    )


# 5. ADD PRODUCT

@role_required('SELLER')
def add_product(request):

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Product added successfully!'
            )

            return redirect('myproducts')

    else:

        form = ProductForm()

    return render(
        request,
        'seller/product_form.html',
        {'form': form, 'title': 'Add Product'}
    )


# 6. MY PRODUCTS

@role_required('SELLER')
def myproducts(request):

    products = Product.objects.all().order_by('-created_at')

    return render(
        request,
        'seller/my_products.html',
        {'products': products}
    )


# 7. EDIT PRODUCT

@role_required('SELLER')
def edit_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Product updated successfully!'
            )

            return redirect('myproducts')

    else:

        form = ProductForm(instance=product)

    return render(
        request,
        'seller/product_form.html',
        {'form': form, 'title': 'Edit Product'}
    )


# 8. DELETE PRODUCT

@role_required('SELLER')
def delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':

        try:
            product.delete()

            messages.success(
                request,
                'Product deleted successfully!'
            )

        except Exception:
            messages.error(
                request,
                'This product is already included in an order. It cannot be deleted.'
            )

    return redirect('myproducts')


# 9. MANAGE BUYER ORDERS

@role_required('SELLER')
def manage_orders(request):

    orders = Order.objects.prefetch_related(
        'items__product'
    ).select_related('user').order_by('-created_at')

    return render(
        request,
        'seller/manage_orders.html',
        {'orders': orders}
    )


# 10. UPDATE ORDER STATUS

@role_required('SELLER')
def update_order_status(request, id):

    order = get_object_or_404(Order, id=id)

    if request.method == 'POST':

        new_status = request.POST.get('status')

        allowed_statuses = [
            'CONFIRMED',
            'SHIPPED',
            'DELIVERED'
        ]

        if new_status in allowed_statuses:

            if order.status not in ['CANCELLED', 'DELIVERED']:

                order.status = new_status

                order.save(update_fields=['status'])

                messages.success(
                    request,
                    'Order status updated!'
                )

            else:

                messages.error(
                    request,
                    'This order cannot be updated.'
                )

    return redirect('manage_orders')





