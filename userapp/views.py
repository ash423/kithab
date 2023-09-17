from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponse
from urllib.parse import urlencode
from django.contrib import messages
from admindash.views import admindash
from cart.models import Cart,CartItem
from store.views import home


# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode





def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)
        if user is not None :
            if user.is_superuser:
                login(request,user)
                return redirect('admindash')

            login(request,user)
            user = request.user
            guest_cart_id=request.session.get('cart_id')
            if guest_cart_id:
                try:
                    guest_cart = Cart.objects.get(id=guest_cart_id)
                    user_cart,created = Cart.objects.get_or_create(user=user)
                    for guest_item in guest_cart.cartitem_set.all():
                        try:
                            user_item=CartItem.objects.get(cart=user_cart,variant=guest_item.variant)
                            available_stock = guest_item.variant.stock - user_item.quantity
                            if guest_item.quantity <= available_stock:
                                user_item.quantity += guest_item.quantity
                                user_item.save()
                            else:
                                messages.error(request,f"Requested quantity for {guest_item.product} exceeds available stock")
                        except CartItem.DoesNotExist:

                            CartItem.objects.create(cart=user_cart,variant=guest_item.variant,quantity=guest_item.quantity,price=guest_item.price)
                    guest_cart.delete()
                    del request.session['cart_id']
                except Cart.DoesNotExist:
                    pass
        else :
            messages.error(request,"Bad Credentials")
            return redirect(signin)
        return redirect(home)

    return render(request,"book_store/login.html")

def loginwithotp(request):
    if request.method == 'POST':
        username = request.POST['username']
        context = {'name':username}
        return render(request,'book_store/otpp.html',context)
    return render(request,'book_store/loginwithotp.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect(signup)
        if User.objects.filter(email=email):
            messages.error(request, "Email Already Registered!!")
            return redirect(signup)
        if len(username)>10:
            return redirect(signup)
        if pass1 != pass2:
            return redirect(signup)

        if not username.isalnum():
            return redirect(signup)

        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        #myuser.is_active = False

        myuser.save()
        #return redirect(signin)

        #Generate verification token
        token = default_token_generator.make_token(myuser)

        # To Build confirmation mail

        current_site =  get_current_site(request)
        uidb64 = urlsafe_base64_encode(force_bytes(myuser.pk))
        verification_url = reverse('verify_email',kwargs={'uidb64': uidb64,'token' : token})
        verification_url =f"{request.scheme}://{current_site.domain}{verification_url}"

        #Send veriication email
        mail_subject = 'Activate your account'
        message = render_to_string('book_store/verification_email.html',{
            'user': myuser,
            'verification_url' : verification_url
        })
        send_mail(mail_subject,message,'kithabnation@gmail.com',[email])

        return redirect('email_confirmation')




    return render(request,"book_store/signup.html")

def signout(request):
    logout(request)
    return redirect('home')
def admindash():
    pass
def verify_email(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user =None
    if user and default_token_generator.check_token(user, token):
        user.is_active =True
        user.save()
        return redirect(signin)

def email_confirmation(request):
    return render(request,'book_store/email_confirmation.html')
