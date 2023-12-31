from django.urls import path,include
from . import views
urlpatterns = [
    path('admindash',views.admindash,name='admindash'),
    path('userslist',views.userslist,name='userslist'),
    path('orderslist',views.orderslist,name='orderslist'),
    path('change_order_status/<int:orderid>/<int:statusid>',views.change_order_status,name='change_order_status'),
    path('block_user/<int:user_id>/', views.block_user , name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user , name='unblock_user'),
    path('adminsignout',views.adminsignout,name='adminsignout'),
    path('variants_list',views.variants_list,name='variants_list'),
    path('add_variant',views.add_variant,name='add_variant'),
    path('edit_variant',views.edit_variant,name='edit_variant'),
    path('productslist',views.productslist,name='productslist'),
    path('categorieslist',views.categorieslist,name='categorieslist'),
    path('addcategory/',views.addcategory,name='addcategory'),
    path('block_product/<int:book_id>/', views.block_product , name='block_product'),
    path('unblock_product/<int:book_id>/', views.unblock_product , name='unblock_product'),
    path('editcategory/<int:category_id>/', views.editcategory , name='editcategory'),
    path('addproduct/',views.addproduct,name='addproduct'),
    path('editproduct/<int:book_id>/', views.editproduct , name='editproduct'),
    path('viewcoupons',views.view_coupons,name= 'view_coupon'),
    path('add_coupon',views.addcoupon,name='add_coupon'),
    path('edit_coupon/<int:coupon_id>',views.edit_coupon,name='edit_coupon'),
    path('disable_coupon/<int:coupon_id>',views.disable_coupon,name='disable_coupon'),
    path('enable_coupon/<int:coupon_id>',views.enable_coupon,name='enable_coupon'),
    path('edit_variant/<int:variant_id>',views.edit_variant,name='edit_variant'),
    path('disable_variant/<int:variant_id>',views.disable_variant,name='disable_variant'),
    path('enable_variant/<int:variant_id>',views.enable_variant,name='enable_variant'),
    path('sales_report',views.sales_report,name='sales_report'),

]