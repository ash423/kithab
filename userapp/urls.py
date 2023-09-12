from django.urls import path,include
from . import views
urlpatterns = [



    path('signin/',views.signin,name='signin'),
    path('signup/',views.signup,name='signup'),
    path('signout/',views.signout,name='signout'),
    path('email_confirmation/',views.email_confirmation,name='email_confirmation'),

    path('verify_email/<str:uidb64>/<str:token>/',views.verify_email,name='verify_email'),
    path('loginwithotp/',views.loginwithotp,name='loginwithotp')



]