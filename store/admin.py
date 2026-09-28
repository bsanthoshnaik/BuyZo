from django.contrib import admin

from .models import (
    Customer,
    Product,
    ProductImage,
    CartItem,
    WishlistItem,
    Address,
    Order,
    OrderItem,
    Payment,
    UPIPayment,
    Banner,
    ProductVariant,
)


admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(CartItem)
admin.site.register(WishlistItem)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(UPIPayment)
admin.site.register(Banner)
admin.site.register(ProductVariant)