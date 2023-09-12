from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_profile, name='user_profile'),
    path('address_management', views.address_management, name='address_management'),
    path('set_as_default/<int:address_id>', views.set_as_default, name='set_as_default'),
    path('delete_address/<int:address_id>', views.delete_address, name='delete_address'),
    path('add_address', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>', views.edit_address, name='edit_address'),
    path('change_password',views.change_password,name='change_password'),
    path('my_wallet',views.My_Wallet,name='my_wallet')

]

