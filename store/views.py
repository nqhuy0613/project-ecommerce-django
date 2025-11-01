
from django.shortcuts import render

from . models import Category, Product

from django.shortcuts import get_object_or_404

# Import DailyRevenue from payment app (maps to `daily_revenue` table)
from payment.models import DailyRevenue
from decimal import Decimal
from django.contrib.admin import site as admin_site
from django.contrib.admin.views.decorators import staff_member_required


def store(request):

    all_products = Product.objects.all()

    context = {'my_products':all_products}

    return render(request, 'store/store.html', context)



def categories(request):

    all_categories = Category.objects.all()

    return {'all_categories': all_categories}



def list_category(request, category_slug=None):

    category = get_object_or_404(Category, slug=category_slug)

    products = Product.objects.filter(category=category)


    return render(request, 'store/list-category.html', {'category':category, 'products':products})



def product_info(request, product_slug):

    product = get_object_or_404(Product, slug=product_slug)

    context = {'product': product, "numbers": range(1, 101)}

    return render(request, 'store/product-info.html', context)


@staff_member_required
def revenue_page(request):
    # lấy các ngày trong bảng doanh thu hàng ngày 
    revenues = DailyRevenue.objects.all()

    # try catch tính tổng
    total = 0
    for r in revenues:
        try:
            total += r.total_revenue
        except Exception:
            
            continue
    context = admin_site.each_context(request)
    context.update({
        'revenues': revenues,
        'total_revenue': total,
        
    })
    return render(request, 'store/revenue.html', context)














 