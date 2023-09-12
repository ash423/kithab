from django.urls import path,include
from . import views
urlpatterns = [

    path('add_to_cart/<int:variant_id>', views.add_to_cart, name='add_to_cart'),
    path('update_quantity', views.update_quantity, name='update_quantity'),
    path('remove_cart_item/<int:cart_item_id>', views.remove_cart_item, name='remove_cart_item'),
    path('wishlist', views.wishlist_summary, name='wishlist_summary'),
    path('add_to_wishlist/<int:variant_id>', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:wishlist_item_id>', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist_to_cart/<int:wishlist_item_id>', views.wishlist_to_cart, name='wishlist_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_placed/<int:addressid>', views.order_placed, name='order_placed'),
    path('pay_using_wallet/<int:addressid>', views.pay_using_wallet, name='pay_using_wallet'),

    path('initiate_payment',views.initiate_payment, name='initiate_payment'),
    path('online_payment_order/<int:add_id>/',views.online_payment_order,name='online_payment_order'),
    path('orderplaced',views.orderplaced,name='orderplaced'),
    path('addaddress_checkout',views.addaddress_checkout,name='addaddress_checkout'),
    path('view_cart',views.view_cart,name='view_cart'),
    path('apply_coupon',views.apply_coupon,name='apply_coupon'),
    path('remove_coupon',views.remove_coupon,name='remove_coupon')

]