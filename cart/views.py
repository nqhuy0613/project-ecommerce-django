from django.shortcuts import render

# from .cart import Cart
from store.models import Product

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

# Create your views here.

def cart_summary(request):
    # cart = Cart(request), {'cart':cart}
    return render(request, "cart/cart-summary.html")