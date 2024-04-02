import json
import decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache, cache_control
from django.http import JsonResponse
from django.db import transaction
from offbeatapp.models import Product, Customer
from shop.forms import AddressForm
from shop.models import Address
from .forms import CouponForm
from .models import Cart, Order, OrderItem, Coupon, Wallet, Wishlist
from django.contrib import messages
from datetime import timedelta

# Create your views here.
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cart(request):
    if "discount" in request.session:
        del request.session["discount"]

    if isinstance(request.user, AnonymousUser):
        device_id = request.COOKIES.get("device_id")
        cart_items = Cart.objects.filter(device=device_id).order_by("id")
    else:
        user = request.user
        cart_items = Cart.objects.filter(user=user).order_by("id")

    subtotal = 0
    total_dict = {}

    for cart_item in cart_items:
        if cart_item.product and cart_item.quantity > cart_item.product.stock:
            messages.warning(
                request,
                f" Product is out of stock . {cart_item.product.stock} left"
            )
            cart_item.quantity = cart_item.product.stock
            cart_item.save()
        elif cart_item.product:
            item_price = cart_item.product.price * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price

    for cart_item in cart_items:
        if cart_item.product:
            cart_item.total_price = total_dict.get(cart_item.id, 0)
            cart_item.save()

    discount = request.session.get("discount", 0)
    shipping_cost = 60
    total = (subtotal + shipping_cost) - discount if subtotal else 0

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "total": total,

    }

    return render(request, "shop/cart.html", context)

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('product_not_found')

    quantity = request.POST.get('quantity', 1)

    if not quantity:
        quantity = 1

    max_quantity_per_person = 2
    if isinstance(request.user, AnonymousUser):
        device_id = request.COOKIES.get('device_id')
        if not device_id:
            messages.warning(request, 'Device ID not found.')
            return redirect('cart')

        cart_item, created = Cart.objects.get_or_create(device=device_id, product=product)
    else:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if not created and cart_item.quantity >= max_quantity_per_person:
        messages.warning(request, f'You have already added the maximum quantity ({max_quantity_per_person}) of this product to your cart.')
        return redirect('cart')
    total_quantity = cart_item.quantity + int(quantity)

    if total_quantity > max_quantity_per_person:
        messages.warning(request, f'You can only add up to {max_quantity_per_person} of this product to your cart.')
        return redirect('cart')

    if created:
        cart_item.quantity = int(quantity)
    else:
        cart_item.quantity += int(quantity)
    cart_item.save()

    return redirect('cart')


def update_cart(request, product_id):
    cart_item = None
    if isinstance(request.user, AnonymousUser):
        device_id = request.COOKIES.get('device_id')
        if not device_id:
            return JsonResponse({'message': 'Device ID not found.'}, status=400)

        cart_item, created = Cart.objects.get_or_create(device=device_id, product_id=product_id)
    else:
        cart_item = get_object_or_404(Cart, product_id=product_id, user=request.user)

    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity'))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'message': 'Invalid quantity.'}, status=400)

    if quantity < 1:
        return JsonResponse({'message': 'Quantity must be at least 1.'}, status=400)

    max_quantity_per_person = 2
    if quantity > max_quantity_per_person:
        messages.error(request, f" You Cannot Purchase More Than {max_quantity_per_person} Products")
        return JsonResponse(
            {'message': f'You can only add up to {max_quantity_per_person} units of this product to your cart.'},
            status=400)

    cart_item.quantity = quantity
    cart_item.save()

    return JsonResponse({'message': 'Cart item updated.'}, status=200)


def remove_from_cart(request, cart_item_id):
    try:
        if isinstance(request.user, AnonymousUser):
            device_id = request.COOKIES.get('device_id')
            if not device_id:
                return JsonResponse({'message': 'Device ID not found.'}, status=400)
            cart_item = Cart.objects.get(id=cart_item_id, device=device_id)
        else:
            cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
        cart_item.delete()
        messages.success(request, "Item removed from cart successfully.")
    except Cart.DoesNotExist:
        pass

    return redirect('cart')


def wishlist_view(request):
    user = request.user
    if isinstance(user, AnonymousUser):

        device_id = request.COOKIES.get('device_id')
        if not device_id:
            return JsonResponse({'message': 'Device ID not found.'}, status=400)
        wishlist_items = Wishlist.objects.filter(device=device_id)
    else:
        wishlist_items = Wishlist.objects.filter(user=user)

    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'wishlist.html', context)

def add_to_wishlist(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('product_not_found')

    user = request.user
    if isinstance(user, AnonymousUser):
        device_id = request.COOKIES.get('device_id')
        if not device_id:
            return JsonResponse({'message': 'Device ID not found.'}, status=400)
        wishlist, created = Wishlist.objects.get_or_create(product=product, device=device_id)
    else:
        wishlist, created = Wishlist.objects.get_or_create(product=product, user=user)
    wishlist.save()

    return redirect('wishlist_view')

def remove_from_wishlist(request, wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, pk=wishlist_id, user=request.user)
    product_name = wishlist_item.product.product_name
    wishlist_item.delete()
    messages.success(request, f"{product_name} removed from your wishlist.")
    return redirect('wishlist_view')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='signup')  # Use the login_required decorator
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    addresses = Address.objects.filter(user=user, is_deleted=False)
    subtotal = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
    shipping_cost = 60
    discount = request.session.get("discount", 0)
    grand_total = subtotal + shipping_cost - discount
    address_form = AddressForm()
    if request.method == 'POST':
        if 'address_id' in request.POST:
            address_id = request.POST['address_id']
            address_instance = Address.objects.get(id=address_id)
            address_form = AddressForm(request.POST, instance=address_instance)
        else:
            address_form = AddressForm(request.POST)
        if address_form.is_valid():
            new_address = address_form.save(commit=False)
            new_address.user = user
            new_address.save()
            return redirect('checkout')
    context = {
        'cart_items': cart_items,
        'addresses': addresses,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'address_form': address_form,
        'grand_total': grand_total,
        'discount': discount,
    }
    return render(request, 'checkout.html', context)


@login_required
def placeorder(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    subtotal = 0
    for cart_item in cart_items:
        itemprice2 = (cart_item.product.price) * (cart_item.quantity)
        subtotal += itemprice2

    shipping_cost = 60
    total = subtotal + shipping_cost if subtotal else 0

    discount = request.session.get("discount", 0)

    if request.method == "POST":
        payment = request.POST.get("payment")
        address_id = request.POST.get("addressId")

        if not address_id:
            messages.info(request, "Select Address!!!")
            return redirect("checkout")
        if not payment:
            messages.info(request, "Select Payment !!!")
            return redirect("checkout")

        if discount:
            total -= discount

        address = Address.objects.get(id=address_id)

        # Check if the total amount is greater than 2000 and payment method is COD
        if total > 2000 and payment == "cod":
            messages.error(request, "Orders above Rs 2000 are not eligible for Cash on Delivery.")
            return redirect("checkout")  # Or any other redirect URL

        order = Order.objects.create(
            user=user,
            address=address,
            amount=total,
            payment_type=payment,
        )
        # Create or update wallet record

        for cart_item in cart_items:
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()

            order_item = OrderItem.objects.create(
                order=order,
                product=product,  # associate the OrderItem with the Product
                quantity=cart_item.quantity,
                image=product.image,  # Product model has an 'image' field
            )

        cart_items.delete()
        return redirect("order_success")


@login_required
def ordersuccess(request):
    orders = Order.objects.order_by("-id")[:1]

    context = {
        "orders": orders,
    }
    return render(request, "ordersuccess.html", context)


@login_required
def my_orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-id')
    for order in user_orders:
        order.expected_delivery_date = order.date + timedelta(days=7)
    context = {
        'user_orders': user_orders,
    }
    return render(request, 'myorders.html', context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.expected_delivery_date = order.date + timedelta(days=7)
    total = sum(order_item.product.price * order_item.quantity for order_item in order.orderitem_set.all())
    subtotal = sum(order_item.product.price * order_item.quantity for order_item in order.orderitem_set.all())
    shipping = 60
    discount = request.session.get("discount", 0)

    grand_total = subtotal + shipping - discount
    order_items = order.orderitem_set.all()
    for order_item in order_items:
        order_item.total = order_item.product.price * order_item.quantity

    context = {
        'order': order,
        'discount': discount,
        'total': total,
        'subtotal': subtotal,
        'shipping': shipping,
        'grand_total': grand_total,
        'order_items': order_items,

    }
    return render(request, 'order_detail.html', context)


def order_invoice(request, order_id):
    # Get the current user's Customer instance
    user = request.user
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        coupon_code = request.session.get('coupon_code')
        coupon = None

        if coupon_code:
            try:
                coupon = Coupon.objects.get(coupon_code=coupon_code)
            except Coupon.DoesNotExist:
                pass

        cart_items = Cart.objects.filter(user=request.user)

        subtotal = sum(order_item.product.price * order_item.quantity for order_item in order_items)
        shipping = 60
        discount = coupon.discount if coupon else 0
        grand_total = subtotal + shipping - discount
        order_items = order.orderitem_set.all()
        for order_item in order_items:
            order_item.total = order_item.product.price * order_item.quantity

        context = {
            'user': user,
            'order': order,
            'order_items': order_items,
            'grand_total': grand_total,
            'cart_items': cart_items,
            'discount': discount,
            'subtotal': subtotal,
            'shipping': shipping
        }

    except Order.DoesNotExist:
        messages.error(request, 'Order does not exist.')
        return redirect('product_list')

    return render(request, 'invoice_template.html', context)


def user_cancel_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        user = request.user
        try:
            wallets = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            wallets = Wallet.objects.create(user=user)

        try:
            order = Order.objects.get(id=order_id, user=request.user)

            if order.status in ['pending', 'processing']:

                order.status = 'cancelled'
                order.save()
                if order.payment_type != 'cod':
                    wallets.amount += int(order.amount)
                    wallets.save()
                messages.success(request,
                                 'Order canceled successfully.Dont worry ...Your Paid Amount refunded to wallet.')
            else:
                messages.error(request, 'Cannot cancel the order with the current status.')


        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')

    return redirect('my_orders')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def coupon(request):
    if "admin" in request.session:
        coupons = Coupon.objects.all().order_by("id")
        couponform = CouponForm()
        context = {"coupons": coupons, "couponform": couponform}
        return render(request, "admin/coupon.html", context)
    else:
        return redirect("admin")


def addcoupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect('coupon')


def apply_coupon(request):
    if request.method == "POST":
        if 'coupon_code' in request.POST:
            coupon_code = request.POST.get("coupon_code")

            if coupon_code:  # Check if a coupon code was provided coupon from adminside
                try:
                    coupon = Coupon.objects.get(coupon_code=coupon_code)
                except Coupon.DoesNotExist:
                    messages.error(request, "Invalid coupon code")
                    return redirect("cart")

                user = request.user
                cart_items = Cart.objects.filter(user=user)
                subtotal = 0
                shipping_cost = 10
                total_dict = {}
                coupons = Coupon.objects.all()

                for cart_item in cart_items:
                    if cart_item.quantity > cart_item.product.stock:
                        messages.warning(
                            request, f"{cart_item.product.product_name} is out of stock."
                        )
                        cart_item.quantity = cart_item.product.stock
                        cart_item.save()

                    else:
                        item_price = cart_item.product.price * cart_item.quantity
                        total_dict[cart_item.id] = item_price
                        subtotal += item_price

                if subtotal >= coupon.minimum_amount:
                    messages.success(request, "Coupon applied successfully")
                    request.session["discount"] = coupon.discount_price
                    total = subtotal - coupon.discount_price + shipping_cost
                else:
                    messages.error(request, "Coupon not available for this price")
                    total = subtotal + shipping_cost

                for cart_item in cart_items:
                    cart_item.total_price = total_dict.get(cart_item.id, 0)
                    cart_item.save()

                context = {
                    "cart_items": cart_items,
                    "subtotal": subtotal,
                    "total": total,
                    "coupons": coupons,
                    "discount_amount": coupon.discount_price,
                }

                return render(request, "shop/cart.html", context)
        elif 'remove_coupon' in request.POST:
            if 'discount' in request.session:
                del request.session['discount']
                messages.success(request, "Coupon removed successfully")
            else:
                messages.error(request, "No coupon applied to remove")

    return redirect("cart")


@login_required
def wallet(request):
    user = request.user
    try:
        wallets = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        wallets = Wallet.objects.create(user=user)
    wallet_amount = wallets.amount

    context = {'wallet_amount': wallet_amount}

    return render(request, 'wallet.html', context)

@login_required
def pay_with_wallet(request):
    try:
        with transaction.atomic():
            user = request.user
            wallet = Wallet.objects.get(user=user)
            cart_items = Cart.objects.filter(user=user)
            total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
            shipping = 60
            discount = request.session.get("discount", 0)
            subtotal = total + shipping - discount
            order_total = decimal.Decimal(str(subtotal))
            address = Address.objects.filter(user=user, is_deleted=False).first()

            payment_type = "Wallet"
            order = Order.objects.create(
                user=user,
                address=address,
                amount=total,
                payment_type=payment_type,
            )

            for cart_item in cart_items:
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    image=product.image,
                )

            if wallet.amount >= order_total and order_total > 0:
                wallet.amount -= order_total
                wallet.save()
                cart_items.delete()
                messages.success(request, 'Payment successful!')
                return redirect('order_success')
            else:
                messages.error(request, 'Insufficient wallet balance !')
    except Wallet.DoesNotExist:
        messages.error(request, 'Wallet not found for this user!')
    except Address.DoesNotExist:
        messages.error(request, 'Address not found for this user!')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return redirect('checkout')

def proceedtopay(request):
    cart = Cart.objects.filter(user=request.user)
    cart_items = Cart.objects.filter(user=request.user)
    total = 0
    shipping = 60
    subtotal = 0
    for cart_item in cart:
        itemprice = (cart_item.product.price) * (cart_item.quantity)

        subtotal = subtotal + itemprice

    total = subtotal + shipping
    return JsonResponse({"total": total})

def razorpay(request, address_id):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal = 0
    for cart_item in cart_items:
        itemprice = (cart_item.product.price) * (cart_item.quantity)

        subtotal = subtotal + itemprice

    shipping_cost = 60
    total = subtotal + shipping_cost if subtotal else 0

    payment = "razorpay"
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    address = Address.objects.get(id=address_id)

    order = Order.objects.create(
        user=user,
        address=address,
        amount=total,
        payment_type=payment,
    )

    for cart_item in cart_items:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()

        order_item = OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            image=cart_item.product.image,
        )

    cart_items.delete()
    return redirect("order_success")
