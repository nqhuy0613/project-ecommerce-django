from django.shortcuts import render

from . models import Category, Product

from django.shortcuts import get_object_or_404

from django.db import connection

from payment.models import DailyRevenue

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



def search_products(request):
    query = request.GET.get('q', '').strip()
    product = None

    if query:
        with connection.cursor() as cursor:
            cursor.callproc('SearchProducts', [query])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

            if row:
                data = dict(zip(columns, row))
                product = Product(**data)
            else:
                return render(request, 'store/no-product.html', {'query': query})
    else:
        return render(request, 'store/no-product.html', {'query': query})

    return render(request, 'store/product-info.html', {'product': product})




def sort_category(request, category_slug):
    sort_type = request.GET.get('type')
    category = get_object_or_404(Category, slug=category_slug)

    product_ids = []

    if sort_type in ['asc', 'desc', 'new' ,'bestseller']:
        with connection.cursor() as cursor:
            cursor.callproc('SortProducts', [category.id, sort_type])
            rows = cursor.fetchall()
            product_ids = [row[0] for row in rows]
    products = Product.objects.filter(id__in=product_ids, category=category)
    if product_ids:
        products = sorted(products, key=lambda x: product_ids.index(x.id))
    return render(request, 'store/list-category.html', {
        'category': category,
        'products': products,
    })

def filter_price_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    min_price = int(request.GET.get('min_price', 0))
    max_price = int(request.GET.get('max_price', 999999999))

    product_ids = []

    with connection.cursor() as cursor:
        cursor.callproc('sp_filter_products', [category.id, min_price, max_price])
        rows = cursor.fetchall()
        product_ids = [row[0] for row in rows]  # giả sử SP trả về id sản phẩm

    products = Product.objects.filter(id__in=product_ids, category=category)

    if product_ids:
        products = sorted(products, key=lambda x: product_ids.index(x.id))
    else:
        return render(request, 'store/no-product.html')

    return render(request, 'store/list-category.html', {
        'category': category,
        'products': products,
    })


@staff_member_required
def revenue_page(request):
    # lấy các ngày trong bảng doanh thu hàng ngày
    revenues = DailyRevenue.objects.all().order_by('-date')

    # try except tính tổng
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














