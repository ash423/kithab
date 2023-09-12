from django.urls import path,include
from . import views
urlpatterns = [

    path('view_order/<int:orderid>', views.view_order, name='view_order'),
    path('view_orders/<int:orderid>', views.view_orders, name='view_orders'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('return_order/<int:order_id>/', views.return_order, name='return_order'),
    path('download_invoice/<int:order_id>',views.download_invoice,name='download_invoice'),
    path('my_orders',views.my_orders,name='my_orders')

]