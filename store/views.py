from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
import uuid
import random
import time
import re

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import (
    Customer,
    Product,
    ProductVariant,
    ProductImage,
    CartItem,
    WishlistItem,
    Address,
    Order,
    OrderItem,
    Payment,
    UPIPayment,
    Banner,
)


# GET LOGGED-IN CUSTOMER

def get_customer(request):

    customer_id = request.session.get("customer_id")

    if not customer_id:
        return None

    try:
        return Customer.objects.get(
            id=customer_id
        )
    except Customer.DoesNotExist:
        return None


# ACCOUNT

def account(request):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    addresses = Address.objects.filter(
        customer=customer,
        is_active=True
    ).order_by("-created_at")

    orders = Order.objects.filter(
        customer=customer
    ).select_related(
        "address"
    ).prefetch_related(
        "items__product"
    ).order_by("-created_at")

    wishlist_count = WishlistItem.objects.filter(
        customer=customer
    ).count()

    cart_count = CartItem.objects.filter(
        customer=customer
    ).count()

    return render(
        request,
        "store/account.html",
        {
            "customer": customer,
            "addresses": addresses,
            "orders": orders,
            "wishlist_count": wishlist_count,
            "cart_count": cart_count,
        }
    )


# HOME

def home(request):

    customer = get_customer(request)

    # PRODUCTS

    products = Product.objects.all().order_by("-id")

    # BANNERS

    banners = Banner.objects.filter(
        is_active=True
    ).order_by(
        "display_order",
        "-id"
    )

    # CATEGORY FILTER

    category = request.GET.get(
        "category"
    )

    if category:

        products = products.filter(
            category=category
        )

    # SEARCH

    search = request.GET.get(
        "search"
    )

    if search:

        search = search.strip()

        if search:

            products = products.filter(
                Q(name__icontains=search)
                |
                Q(category__icontains=search)
            )

    # WISHLIST

    wishlist_product_ids = []

    if customer:

        wishlist_product_ids = list(
            WishlistItem.objects.filter(
                customer=customer
            ).values_list(
                "product_id",
                flat=True
            )
        )

    # HOME PAGE

    return render(
        request,
        "store/home.html",
        {
            "customer": customer,
            "products": products,
            "banners": banners,
            "wishlist_product_ids": wishlist_product_ids,
            "search": search,
            "category": category,
        }
    )


# REGISTER

def register(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        login_id = request.POST.get("login_id", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not name:
            messages.error(request, "Please enter your name.")
            return render(request, "store/register.html")

        if not login_id:
            messages.error(request, "Please enter mobile number or email.")
            return render(request, "store/register.html")

        if not password:
            messages.error(request, "Please enter a password.")
            return render(request, "store/register.html")

        if len(password) < 4:
            messages.error(request, "Password must contain at least 4 characters.")
            return render(request, "store/register.html")

        if not confirm_password:
            messages.error(request, "Please confirm your password.")
            return render(request, "store/register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "store/register.html")

        mobile_number = login_id.replace(" ", "")
        is_mobile = re.fullmatch(r"[6-9][0-9]{9}", mobile_number)
        is_email = False

        if not is_mobile:
            try:
                validate_email(login_id)
                is_email = True
            except ValidationError:
                messages.error(request, "Please enter a valid 10-digit mobile number or valid email address.")
                return render(request, "store/register.html")

        if is_mobile:
            login_id = mobile_number
            existing_customer = Customer.objects.filter(
                Q(login_id__iexact=login_id) | Q(mobile=login_id)
            ).first()
        else:
            login_id = login_id.lower()
            existing_customer = Customer.objects.filter(
                Q(login_id__iexact=login_id) | Q(email__iexact=login_id)
            ).first()

        if existing_customer:
            messages.error(request, "This mobile number or email is already registered.")
            return render(request, "store/register.html")

        if is_mobile:
            Customer.objects.create(
                name=name,
                login_id=login_id,
                password=password,
                mobile=login_id,
                email=None
            )
        else:
            Customer.objects.create(
                name=name,
                login_id=login_id,
                password=password,
                mobile=None,
                email=login_id
            )

        messages.success(request, "Registration successful!")
        return redirect("login")

    return render(request, "store/register.html")


# LOGIN

def login_page(request):

    if request.method == "POST":

        login_id = request.POST.get("login_id", "").strip()
        password = request.POST.get("password", "")

        if not login_id:
            messages.error(request, "Please enter your mobile number or email.")
            return render(request, "store/login.html")

        if not password:
            messages.error(request, "Please enter your password.")
            return render(request, "store/login.html")

        normalized_login = login_id.replace(" ", "")

        customer = Customer.objects.filter(
            Q(login_id__iexact=normalized_login)
            | Q(mobile=normalized_login)
            | Q(email__iexact=normalized_login),
            password=password
        ).first()

        if customer:
            request.session["customer_id"] = customer.id
            messages.success(request, f"Welcome back, {customer.name}!")
            return redirect("home")

        messages.error(request, "Invalid mobile/email or password.")
        return render(request, "store/login.html")

    return render(request, "store/login.html")


# LOGOUT

def logout(request):

    request.session.flush()

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect(
        "login"
    )


# CHANGE PASSWORD - START OTP

def forgot_password(request):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    if request.method == "POST":

        login_id = request.POST.get(
            "login_id",
            ""
        ).strip()

        if login_id.lower() != customer.login_id.lower():

            messages.error(
                request,
                "Please enter your registered mobile number or email."
            )

            return render(
                request,
                "store/forgot_password.html",
                {
                    "customer": customer,
                }
            )

        otp = str(
            random.randint(
                100000,
                999999
            )
        )

        request.session["password_otp"] = otp

        request.session["password_otp_customer_id"] = (
            customer.id
        )

        request.session["password_otp_created"] = int(
            time.time()
        )

        request.session["development_otp"] = otp

        messages.success(
            request,
            "OTP generated successfully."
        )

        return redirect(
            "verify_password_otp"
        )

    return render(
        request,
        "store/forgot_password.html",
        {
            "customer": customer,
        }
    )


# VERIFY PASSWORD OTP

def verify_password_otp(request):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    otp = request.session.get(
        "password_otp"
    )

    otp_customer_id = request.session.get(
        "password_otp_customer_id"
    )

    otp_created = request.session.get(
        "password_otp_created"
    )

    if not otp or otp_customer_id != customer.id:

        messages.error(
            request,
            "Please request a new OTP."
        )

        return redirect(
            "forgot_password"
        )

    current_time = int(
        time.time()
    )

    if (
        not otp_created
        or current_time - otp_created > 300
    ):

        request.session.pop(
            "password_otp",
            None
        )

        request.session.pop(
            "password_otp_customer_id",
            None
        )

        request.session.pop(
            "password_otp_created",
            None
        )

        request.session.pop(
            "development_otp",
            None
        )

        messages.error(
            request,
            "OTP expired. Please request a new OTP."
        )

        return redirect(
            "forgot_password"
        )

    if request.method == "POST":

        entered_otp = request.POST.get(
            "otp",
            ""
        ).strip()

        if entered_otp != otp:

            messages.error(
                request,
                "Invalid OTP. Please try again."
            )

            return render(
                request,
                "store/verify_password_otp.html",
                {
                    "customer": customer,
                    "development_otp": request.session.get(
                        "development_otp"
                    ),
                }
            )

        request.session["password_otp_verified"] = True

        request.session.pop(
            "password_otp",
            None
        )

        request.session.pop(
            "password_otp_customer_id",
            None
        )

        request.session.pop(
            "password_otp_created",
            None
        )

        request.session.pop(
            "development_otp",
            None
        )

        return redirect(
            "reset_password"
        )

    return render(
        request,
        "store/verify_password_otp.html",
        {
            "customer": customer,
            "development_otp": request.session.get(
                "development_otp"
            ),
        }
    )


# RESET PASSWORD AFTER OTP VERIFICATION

def reset_password(request):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    otp_verified = request.session.get(
        "password_otp_verified"
    )

    if not otp_verified:

        messages.error(
            request,
            "Please verify OTP before changing your password."
        )

        return redirect(
            "forgot_password"
        )

    if request.method == "POST":

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not password:

            messages.error(
                request,
                "Please enter a new password."
            )

            return render(
                request,
                "store/reset_password.html"
            )

        if len(password) < 4:

            messages.error(
                request,
                "Password must contain at least 4 characters."
            )

            return render(
                request,
                "store/reset_password.html"
            )

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "store/reset_password.html"
            )

        customer.password = password

        customer.save(
            update_fields=["password"]
        )

        request.session.pop(
            "password_otp_verified",
            None
        )

        messages.success(
            request,
            "Password changed successfully. Please login again."
        )

        return redirect(
            "login"
        )

    return render(
        request,
        "store/reset_password.html"
    )


# PRODUCT DETAIL

def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    customer = get_customer(request)

    images = ProductImage.objects.filter(
        product=product
    ).order_by("id")

    # PRODUCT VARIANTS

    variants = ProductVariant.objects.filter(
        product=product,
        is_active=True
    ).order_by("id")

    # WISHLIST

    is_wishlisted = False

    if customer:

        is_wishlisted = WishlistItem.objects.filter(
            customer=customer,
            product=product
        ).exists()

    # RELATED PRODUCTS

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    ).order_by("-id")[:8]

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "images": images,
            "customer": customer,
            "is_wishlisted": is_wishlisted,
            "related_products": related_products,
            "variants": variants,
        }
    )


# CART

def cart(request):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    cart_items = CartItem.objects.filter(
        customer=customer
    ).select_related(
        "product"
    ).order_by("-added_at")

    total = Decimal("0.00")

    for item in cart_items:

        item.line_total = (
            item.product.price
            *
            item.quantity
        )

        total += item.line_total

    return render(
        request,
        "store/cart.html",
        {
            "customer": customer,
            "cart_items": cart_items,
            "total": total,
        }
    )


# ADD TO CART

def add_to_cart(request, product_id):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart_item = CartItem.objects.filter(
        customer=customer,
        product=product
    ).first()

    if cart_item:

        cart_item.quantity += Decimal("1")

        cart_item.save()

    else:

        CartItem.objects.create(
            customer=customer,
            product=product,
            quantity=Decimal("1")
        )

    messages.success(
        request,
        f"{product.name} added to cart."
    )

    return redirect(
        "cart"
    )


# BUY NOW

def buy_now(request, product_id):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart_item = CartItem.objects.filter(
        customer=customer,
        product=product
    ).first()

    if cart_item:

        cart_item.quantity = Decimal("1")

        cart_item.save()

    else:

        CartItem.objects.create(
            customer=customer,
            product=product,
            quantity=Decimal("1")
        )

    return redirect(
        "checkout"
    )


# INCREASE CART QUANTITY

def increase_cart(request, item_id):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        customer=customer
    )

    cart_item.quantity += Decimal("1")

    cart_item.save()

    return redirect(
        "cart"
    )


# DECREASE CART QUANTITY

def decrease_cart(request, item_id):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        customer=customer
    )

    if cart_item.quantity > Decimal("1"):

        cart_item.quantity -= Decimal("1")

        cart_item.save()

    else:

        cart_item.delete()

    return redirect(
        "cart"
    )


# REMOVE FROM CART

def remove_from_cart(request, item_id):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        customer=customer
    )

    product_name = cart_item.product.name

    cart_item.delete()

    messages.success(
        request,
        f"{product_name} removed from cart."
    )

    return redirect(
        "cart"
    )


# WISHLIST

def wishlist(request):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    wishlist_items = WishlistItem.objects.filter(
        customer=customer
    ).select_related(
        "product"
    ).order_by("-added_at")

    return render(
        request,
        "store/wishlist.html",
        {
            "customer": customer,
            "wishlist_items": wishlist_items,
        }
    )


# TOGGLE WISHLIST

def toggle_wishlist(request, product_id):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    product = get_object_or_404(
        Product,
        id=product_id
    )

    wishlist_item = WishlistItem.objects.filter(
        customer=customer,
        product=product
    ).first()

    if wishlist_item:

        wishlist_item.delete()

        messages.success(
            request,
            f"{product.name} removed from wishlist."
        )

    else:

        WishlistItem.objects.create(
            customer=customer,
            product=product
        )

        messages.success(
            request,
            f"{product.name} added to wishlist."
        )

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "home"
        )
    )


# ADD ADDRESS

def add_address(request):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        mobile = request.POST.get(
            "mobile",
            ""
        ).strip()

        house = request.POST.get(
            "house",
            ""
        ).strip()

        street = request.POST.get(
            "street",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        state = request.POST.get(
            "state",
            ""
        ).strip()

        pincode = request.POST.get(
            "pincode",
            ""
        ).strip()

        if not all([
            full_name,
            mobile,
            house,
            street,
            city,
            state,
            pincode,
        ]):

            messages.error(
                request,
                "Please fill all address details."
            )

            return redirect(
                "checkout"
            )

        Address.objects.create(
            customer=customer,
            full_name=full_name,
            mobile=mobile,
            house=house,
            street=street,
            city=city,
            state=state,
            pincode=pincode,
            is_active=True
        )

        messages.success(
            request,
            "Address added successfully."
        )

        return redirect(
            "checkout"
        )

    return redirect(
        "checkout"
    )


# REMOVE ADDRESS

def remove_address(request, address_id):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    address = get_object_or_404(
        Address,
        id=address_id,
        customer=customer
    )

    address.is_active = False

    address.save(
        update_fields=["is_active"]
    )

    messages.success(
        request,
        "Address removed successfully."
    )

    return redirect(
        "checkout"
    )


# CHECKOUT

def checkout(request):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    cart_items = CartItem.objects.filter(
        customer=customer
    ).select_related(
        "product"
    ).order_by("-added_at")

    if not cart_items.exists():

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect(
            "home"
        )

    subtotal = Decimal("0.00")

    for item in cart_items:

        item.line_total = (
            item.product.price
            *
            item.quantity
        )

        subtotal += item.line_total

    delivery_charge = Decimal("0.00")

    if subtotal < Decimal("500.00"):

        delivery_charge = Decimal("40.00")

    total_amount = (
        subtotal
        +
        delivery_charge
    )

    addresses = Address.objects.filter(
        customer=customer,
        is_active=True
    ).order_by("-created_at")

    return render(
        request,
        "store/checkout.html",
        {
            "customer": customer,
            "cart_items": cart_items,
            "addresses": addresses,
            "subtotal": subtotal,
            "delivery_charge": delivery_charge,
            "total_amount": total_amount,
        }
    )


# PLACE ORDER

@transaction.atomic
def place_order(request):

    customer = get_customer(request)

    if customer is None:
        return redirect("login")

    if request.method != "POST":

        return redirect(
            "checkout"
        )

    address_id = request.POST.get(
        "address_id"
    )

    payment_method = request.POST.get(
        "payment_method",
        ""
    ).strip()

    upi_id = request.POST.get(
        "upi_id",
        ""
    ).strip()

    if not address_id:

        messages.error(
            request,
            "Please select a delivery address."
        )

        return redirect(
            "checkout"
        )

    address = get_object_or_404(
        Address,
        id=address_id,
        customer=customer,
        is_active=True
    )

    cart_items = list(
        CartItem.objects.filter(
            customer=customer
        ).select_related(
            "product"
        )
    )

    if not cart_items:

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect(
            "cart"
        )

    subtotal = Decimal("0.00")

    for item in cart_items:

        item.line_total = (
            item.product.price
            *
            item.quantity
        )

        subtotal += item.line_total

    delivery_charge = Decimal("0.00")

    if subtotal < Decimal("500.00"):

        delivery_charge = Decimal("40.00")

    total_amount = (
        subtotal
        +
        delivery_charge
    )

    # PAYMENT VALIDATION

    if payment_method not in [
        "COD",
        "ONLINE",
    ]:

        messages.error(
            request,
            "Please select a payment method."
        )

        return redirect(
            "checkout"
        )

    payment_status = "Pending"

    if payment_method == "ONLINE":

        if not upi_id:

            messages.error(
                request,
                "Please enter your UPI ID."
            )

            return redirect(
                "checkout"
            )

        if "@" not in upi_id:

            messages.error(
                request,
                "Please enter a valid UPI ID."
            )

            return redirect(
                "checkout"
            )

        payment_status = "Pending"

    elif payment_method == "COD":

        upi_id = ""

        payment_status = "Pending"

    # CREATE ORDER

    order_number = (
        "BZ"
        +
        time.strftime("%Y%m%d%H%M%S")
        +
        uuid.uuid4().hex[:6].upper()
    )

    order = Order.objects.create(
        customer=customer,
        address=address,
        order_number=order_number,
        subtotal=subtotal,
        delivery_charge=delivery_charge,
        total_amount=total_amount,
        payment_method=payment_method,
        payment_status=payment_status,
        status="Placed",
    )

    # CREATE ORDER ITEMS

    for item in cart_items:

        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
            total=item.line_total,
        )

    # CREATE PAYMENT RECORD

    Payment.objects.create(
        order=order,
        payment_method=(
            "UPI"
            if payment_method == "ONLINE"
            else "COD"
        ),
        transaction_id=None,
        amount=total_amount,
        status="Pending",
    )

    # CLEAR CART

    CartItem.objects.filter(
        customer=customer
    ).delete()

    messages.success(
        request,
        f"Order {order.order_number} placed successfully!"
    )

    return redirect(
        "order_success",
        order_id=order.id
    )


# ORDER SUCCESS

def order_success(request, order_id):

    customer = get_customer(request)

    if customer is None:
        return redirect(
            "login"
        )

    order = get_object_or_404(
        Order.objects
        .select_related(
            "address"
        )
        .prefetch_related(
            "items__product"
        ),
        id=order_id,
        customer=customer
    )

    return render(
        request,
        "store/order_success.html",
        {
            "customer": customer,
            "order": order,
        }
    )


# MY ORDERS

def orders(request):

    customer = get_customer(request)

    if customer is None:
        return redirect(
            "login"
        )

    customer_orders = (
        Order.objects
        .filter(
            customer=customer
        )
        .select_related(
            "address"
        )
        .prefetch_related(
            "items__product"
        )
        .order_by(
            "-created_at"
        )
    )

    return render(
        request,
        "store/orders.html",
        {
            "customer": customer,
            "orders": customer_orders,
        }
    )


# ORDER DETAIL

def order_detail(request, order_id):

    customer = get_customer(request)

    if customer is None:
        return redirect(
            "login"
        )

    order = get_object_or_404(
        Order.objects
        .select_related(
            "address"
        )
        .prefetch_related(
            "items__product"
        ),
        id=order_id,
        customer=customer
    )

    return render(
        request,
        "store/order_detail.html",
        {
            "customer": customer,
            "order": order,
        }
    )