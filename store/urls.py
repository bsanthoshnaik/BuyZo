from django.urls import path
from . import views


# =========================================================
# URL PATTERNS
# =========================================================

urlpatterns = [

    # =====================================================
    # REGISTER / LOGIN
    # =====================================================

    path(
        "",
        views.register,
        name="register"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login_page,
        name="login"
    ),

    path(
        "logout/",
        views.logout,
        name="logout"
    ),

    # =====================================================
    # HOME
    # =====================================================

    path(
        "home/",
        views.home,
        name="home"
    ),

    # =====================================================
    # ACCOUNT
    # =====================================================

    path(
        "account/",
        views.account,
        name="account"
    ),

    # =====================================================
    # ORDERS
    # =====================================================

    path(
        "orders/",
        views.orders,
        name="orders"
    ),

    path(
        "orders/<int:order_id>/",
        views.order_detail,
        name="order_detail"
    ),

    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),

    # =====================================================
    # FORGOT PASSWORD
    # =====================================================

    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password"
    ),

    path(
        "verify-password-otp/",
        views.verify_password_otp,
        name="verify_password_otp"
    ),

    path(
        "reset-password/",
        views.reset_password,
        name="reset_password"
    ),

    # =====================================================
    # PRODUCT
    # =====================================================

    path(
        "product/<int:product_id>/",
        views.product_detail,
        name="product_detail"
    ),

    # =====================================================
    # CART
    # =====================================================

    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "add-to-cart/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "buy-now/<int:product_id>/",
        views.buy_now,
        name="buy_now"
    ),

    path(
        "cart/increase/<int:item_id>/",
        views.increase_cart,
        name="increase_cart"
    ),

    path(
        "cart/decrease/<int:item_id>/",
        views.decrease_cart,
        name="decrease_cart"
    ),

    path(
        "cart/remove/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    # =====================================================
    # CHECKOUT
    # =====================================================

    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    # =====================================================
    # ADDRESS
    # =====================================================

    path(
        "add-address/",
        views.add_address,
        name="add_address"
    ),

    path(
        "remove-address/<int:address_id>/",
        views.remove_address,
        name="remove_address"
    ),

    # =====================================================
    # PLACE ORDER
    # =====================================================

    path(
        "place-order/",
        views.place_order,
        name="place_order"
    ),

    # =====================================================
    # WISHLIST
    # =====================================================

    path(
        "wishlist/",
        views.wishlist,
        name="wishlist"
    ),

    path(
        "wishlist/toggle/<int:product_id>/",
        views.toggle_wishlist,
        name="toggle_wishlist"
    ),
]