from django.contrib import admin

from . models import ShippingAddress, Order, OrderItem, DailyRevenue
# Register your models here.


admin.site.register(ShippingAddress)

admin.site.register(Order)

admin.site.register(OrderItem)

admin.site.register(DailyRevenue)
