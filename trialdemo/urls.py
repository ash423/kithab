from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.trialhome, name='trialhome'),
    path('product_list/<str:category>/<int:cateegoryid>', views.product_list, name='product_list'),

]