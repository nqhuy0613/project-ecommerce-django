from django.shortcuts import render

from . models import Category, Product

from django.shortcuts import get_object_or_404

from django.db import connection


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














