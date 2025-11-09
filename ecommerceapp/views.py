from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import Product, Contact, Order, OrderItem

import razorpay
from decimal import Decimal
from math import ceil
from django.views.decorators.csrf import csrf_exempt


# ================================
# FIX: SAFE Razorpay Initialization
# ================================
def get_razorpay_client():
    """Lazy initialize Razorpay client — prevents server crash on import."""
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


# ================================
# HOME
# ================================
def index(request):
    products = Product.objects.all()
    cols = [[], [], [], []]
    for idx, prod in enumerate(products):
        cols[idx % 4].append(prod)

    return render(request, "index.html", {"columns": cols})


# ================================
# CONTACT FORM
# ================================
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        desc = request.POST.get("desc")
        pnumber = request.POST.get("pnumber")

        Contact.objects.create(
            name=name,
            email=email,
            desc=desc,
            phonenumber=pnumber
        )

        messages.success(request, "We will get back to you soon.")
        return redirect("contact")

    return render(request, "contact.html")


# ================================
# ABOUT
# ================================
def about(request):
    return render(request, "about.html")


# ================================
# PRODUCT DETAIL
# ================================
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})


# ================================
# ADD TO CART (AJAX)
# ================================
@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        prod_id = request.POST.get('product_id')

        try:
            product = Product.objects.get(id=prod_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})

        cart = request.session.get('cart', {})
        cart[prod_id] = cart.get(prod_id, 0) + 1
        request.session['cart'] = cart

        return JsonResponse({
            'success': True,
            'name': product.product_name,
            'price': str(product.price),
            'img': product.image.url,
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# ================================
# CART VIEW
# ================================
def Shop_cart(request):
    cart = request.session.get('cart', {})

    products = Product.objects.filter(id__in=[int(pk) for pk in cart.keys()])
    cart_items = []
    cart_total = Decimal(0)

    if request.method == "POST":
        if 'remove' in request.POST:
            prod_id = request.POST.get('remove')
            cart.pop(prod_id, None)
            request.session['cart'] = cart

        elif 'update_cart' in request.POST:
            for product in products:
                qty_field = f"qty_{product.id}"
                if qty_field in request.POST:
                    try:
                        qty = int(request.POST[qty_field])
                    except ValueError:
                        qty = 0

                    if qty > 0:
                        cart[str(product.id)] = qty
                    else:
                        cart.pop(str(product.id), None)

            request.session['cart'] = cart

    # Recalculate totals
    products = Product.objects.filter(id__in=[int(pk) for pk in cart.keys()])
    cart_items = []
    cart_total = Decimal(0)

    for product in products:
        quantity = cart.get(str(product.id), 0)
        subtotal = product.price * quantity
        cart_total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return render(request, "shop_cart.html", {
        'cart_items': cart_items,
        'cart_total': cart_total
    })


# ================================
# ORDER COMPLETE PAGE
# ================================
def Shop_order_complete(request):
    return render(request, "shop_order_complete.html")


# ================================
# CHECKOUT (CREATE ORDER + RAZORPAY)
# ================================
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=[int(k) for k in cart.keys()])

    if not products.exists():
        return render(request, 'checkout.html', {'cart_items': [], 'cart_total': 0})

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        province = request.POST.get('province')

        total_amount = Decimal(0)
        for product in products:
            quantity = cart.get(str(product.id), 0)
            total_amount += product.price * quantity

        # Create order in DB
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postcode=postcode,
            province=province,
            paid=False
        )

        # Create OrderItems
        for product in products:
            quantity = cart.get(str(product.id), 0)
            if quantity > 0:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

        # Razorpay
        client = get_razorpay_client()
        amount_in_paise = int(total_amount * Decimal("100"))

        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": "0",
        })

        order.razorpay_order_id = razorpay_order['id']
        order.save()

        # Clear cart
        request.session['cart'] = {}

        return render(request, "payment.html", {
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'amount': amount_in_paise,
            'display_amount': total_amount,
            'currency': 'INR',
            'callback_url': '/paymenthandler/',
        })

    # GET request – show summary
    cart_items = []
    cart_total = Decimal(0)

    for product in products:
        quantity = cart.get(str(product.id), 0)
        subtotal = product.price * quantity
        cart_total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })


# ================================
# PAYMENT HANDLER
# ================================
@csrf_exempt
def paymenthandler(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        params = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        client = get_razorpay_client()

        try:
            client.utility.verify_payment_signature(params)

            order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)

            subtotal = sum(item.price * item.quantity for item in order.items.all())
            amount_in_paise = int(subtotal * Decimal("100"))

            client.payment.capture(payment_id, amount_in_paise)

            order.paid = True
            order.razorpay_payment_id = payment_id
            order.razorpay_signature = signature
            order.save()

            vat = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
            total = subtotal + vat

            return render(request, "paymentsuccess.html", {
                "order": order,
                "order_subtotal": subtotal,
                "order_vat": vat,
                "order_total": total
            })

        except razorpay.errors.SignatureVerificationError:
            return render(request, "paymentfail.html")

    return HttpResponseBadRequest("Invalid Request Method")


# ================================
# ACCOUNT DASHBOARD
# ================================
@login_required
def account_dashboard(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, "account_dashboard.html", {
        "user": request.user,
        "orders": user_orders
    })


@login_required
def account_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "account_orders.html", {"orders": orders})
