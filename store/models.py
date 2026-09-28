from django.db import models


# =========================================================
# CUSTOMER
# =========================================================

class Customer(models.Model):

    name = models.CharField(
        max_length=100
    )

    login_id = models.CharField(
        max_length=150,
        unique=True
    )

    password = models.CharField(
        max_length=128
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    mobile = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


# =========================================================
# PRODUCT
# =========================================================

class Product(models.Model):

    CATEGORY_CHOICES = [
        ("Food", "Food"),
        ("Grocery", "Grocery"),
        ("Books", "Books"),
        ("Medicine", "Medicine"),
        ("Electronics", "Electronics"),
        ("Fashion", "Fashion"),
    ]

    name = models.CharField(
        max_length=150
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.CharField(
        max_length=20,
        default="1 kg"
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


# =========================================================
# PRODUCT VARIANT
# =========================================================

class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    name = models.CharField(
        max_length=100
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.name}"


# =========================================================
# PRODUCT IMAGES
# =========================================================

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="products/"
    )

    def __str__(self):
        return self.product.name


# =========================================================
# CART ITEM
# =========================================================

class CartItem(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.customer.name} - "
            f"{self.product.name}"
        )


# =========================================================
# WISHLIST
# =========================================================

class WishlistItem(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "customer",
                    "product"
                ],
                name="unique_customer_product_wishlist"
            )
        ]

    def __str__(self):

        return (
            f"{self.customer.name} - "
            f"{self.product.name}"
        )


# =========================================================
# ADDRESS
# =========================================================

class Address(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=100
    )

    mobile = models.CharField(
        max_length=15
    )

    house = models.CharField(
        max_length=200
    )

    street = models.CharField(
        max_length=200
    )

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.full_name} - "
            f"{self.city}"
        )


# =========================================================
# ORDER
# =========================================================

class Order(models.Model):

    PAYMENT_CHOICES = [
        ("COD", "Cash on Delivery"),
        ("ONLINE", "Online Payment"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE
    )

    order_number = models.CharField(
        max_length=30,
        unique=True
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES
    )

    payment_status = models.CharField(
        max_length=20
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.order_number


# =========================================================
# ORDER ITEM
# =========================================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):

        return self.product.name


# =========================================================
# PAYMENT
# =========================================================

class Payment(models.Model):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    payment_method = models.CharField(
        max_length=30
    )

    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"Payment - Order #{self.order.id}"


# =========================================================
# UPI PAYMENT
# =========================================================

class UPIPayment(models.Model):

    app_name = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    upi_id = models.CharField(
        max_length=100
    )

    qr_image = models.ImageField(
        upload_to="upi/"
    )

    def __str__(self):

        return self.app_name


# =========================================================
# BANNER
# =========================================================

class Banner(models.Model):

    CATEGORY_CHOICES = [
        ("Food", "Food"),
        ("Grocery", "Grocery"),
        ("Medicine", "Medicine"),
        ("Books", "Books"),
        ("Electronics", "Electronics"),
        ("Fashion", "Fashion"),
    ]

    title = models.CharField(
        max_length=100
    )

    category = models.CharField(
        max_length=50
    )

    image = models.ImageField(
        upload_to="banners/"
    )

    is_active = models.BooleanField(
        default=True
    )

    display_order = models.PositiveIntegerField(
        default=1
    )

    def __str__(self):

        return f"{self.title} - {self.category}"