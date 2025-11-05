from django.urls import path

from . import views

urlpatterns = [


    # Store main page

    path('', views.store, name='store'),


    # Individual product

    path('product/<slug:product_slug>/', views.product_info, name='product-info'),


    # Individual category

    path('search/<slug:category_slug>/', views.list_category, name='list-category'),



# revenue page

    path('revenue/', views.revenue_page, name='revenue-page'),


    # tìm kiếm
    path('search/', views.search_products, name='search-products'),

    #sắp xếp
    path('search/<slug:category_slug>/sort/', views.sort_category, name='sort-category'),


    #lọc
    path('search/<slug:category_slug>/filter/', views.filter_price_category, name='filter-price-category'),
]