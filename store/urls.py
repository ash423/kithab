from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('shop/<int:category_id>',views.shop,name='shop'),
    path('trial',views.trial,name="trial"),
    path('product_details/<int:book_id>/<int:variantid>',views.product_details,name='product_details'),
    path('applyfilter',views.applyfilter,name='applyfilter'),
    path('search',views.search,name='search'),
    path('sort/<int:sort_id>',views.sort,name='sort')

    ]



