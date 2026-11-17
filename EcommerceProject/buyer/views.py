from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.views.decorators.http import require_POST

from seller.models import Product
from seller.decorators import role_required

from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm


# 1. BUYER HOME

@role_required('BUYER')
def home(request):

    products = Product.objects.filter(
        stock__gt=0
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()

    if search:

        products = products.filter(
            name__icontains=search
        )

    return render(
        request,
        'buyer/home.html',
        {'products': products}
    )


# 2. ADD TO CART

@role_required('BUYER')
@require_POST
def add_to_cart(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    if product.stock <= 0:

        messages.error(request, 'Product is out of stock!')

        return redirect('home')

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:

        if item.quantity < product.stock:

            item.quantity += 1

            item.save()

        else:

            messages.error(
                request,
                'Available stock limit reached!'
            )

            return redirect('cart')

    messages.success(
        request,
        'Product added to cart!'
    )

    return redirect('cart')


# 3. VIEW CART

@role_required('BUYER')
def cart(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    items = cart.items.select_related('product')

    total = sum(
        item.subtotal() for item in items
    )

    return render(
        request,
        'buyer/cart.html',
        {
            'cart': cart,
            'items': items,
            'total': total
        }
    )


# 4. UPDATE CART QUANTITY

@role_required('BUYER')
@require_POST
def update_cart(request, id):

    item = get_object_or_404(
        CartItem,
        id=id,
        cart__user=request.user
    )

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        messages.error(request, 'Invalid quantity!')
        return redirect('cart')

    if quantity < 1:

        messages.error(request, 'Quantity must be at least 1!')

    elif quantity > item.product.stock:

        messages.error(request, 'Not enough stock!')

    else:

        item.quantity = quantity

        item.save()

        messages.success(request, 'Cart updated!')

    return redirect('cart')


# 5. REMOVE FROM CART

@role_required('BUYER')
@require_POST
def remove_from_cart(request, id):

    item = get_object_or_404(
        CartItem,
        id=id,
        cart__user=request.user
    )

    item.delete()

    messages.success(
        request,
        'Product removed from cart!'
    )

    return redirect('cart')


# 6. CHECKOUT

@role_required('BUYER')
def checkout(request):

    cart = get_object_or_404(
        Cart.objects.prefetch_related('items__product'),
        user=request.user
    )

    items = list(cart.items.all())

    if not items:

        messages.error(request, 'Your cart is empty!')

        return redirect('cart')

    total = sum(
        item.subtotal() for item in items
    )

    if request.method == 'POST':

        form = CheckoutForm(request.POST)

        if form.is_valid():

            try:

                with transaction.atomic():

                    # Lock products while checking stock
                    locked_products = {}

                    for item in items:

                        product = Product.objects.select_for_update().get(
                            id=item.product_id
                        )

                        if product.stock < item.quantity:

                            raise ValueError(
                                f'Insufficient stock for {product.name}'
                            )

                        locked_products[product.id] = product

                    order = Order.objects.create(

                        user=request.user,

                        address=form.cleaned_data['address'],

                        phone=form.cleaned_data['phone'],

                        total_amount=total,

                        payment_method=form.cleaned_data['payment_method']

                    )

                    for item in items:

                        product = locked_products[item.product_id]

                        OrderItem.objects.create(

                            order=order,

                            product=product,

                            quantity=item.quantity,

                            price=product.price

                        )

                        product.stock -= item.quantity

                        product.save(update_fields=['stock'])

                    cart.items.all().delete()

                messages.success(
                    request,
                    'Order placed successfully!'
                )

                return redirect('myorders')

            except ValueError as error:

                messages.error(request, str(error))

            except Product.DoesNotExist:

                messages.error(
                    request,
                    'A product is no longer available.'
                )

    else:

        form = CheckoutForm(initial={
            'phone': request.user.phone
        })

    return render(
        request,
        'buyer/checkout.html',
        {
            'form': form,
            'items': items,
            'total': total
        }
    )


# 7. MY ORDERS

@role_required('BUYER')
def myorders(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        'items__product'
    ).order_by('-created_at')

    return render(
        request,
        'buyer/myorders.html',
        {'orders': orders}
    )


# 8. CANCEL ORDER

@role_required('BUYER')
@require_POST
def cancel_order(request, id):

    with transaction.atomic():

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=id,
            user=request.user
        )

        if order.status != 'PENDING':

            messages.error(
                request,
                'Only pending orders can be cancelled!'
            )

        else:

            order_items = list(
                order.items.select_related('product')
            )

            for item in order_items:

                product = Product.objects.select_for_update().get(
                    id=item.product_id
                )

                product.stock += item.quantity

                product.save(update_fields=['stock'])

            order.status = 'CANCELLED'

            order.save(update_fields=['status'])

            messages.success(
                request,
                'Order cancelled successfully!'
            )

    return redirect('myorders')