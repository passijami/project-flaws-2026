from django.contrib import admin
from .models import Product, Order, Coupon, ImportedOrder

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(ImportedOrder)
