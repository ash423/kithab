import re

from django.shortcuts import render,redirect
from userprofile.models import Address,Wallet,WalletTransaction
from django.contrib import messages


# Create your views here.
def user_profile(request):
    address = Address.objects.filter(user_id=request.user.id,is_default=True).first()
    return render(request, 'user_profile/user_profile.html', {'address':address})


def address_management(request):
    addresses = Address.objects.filter(user=request.user,is_active=True).order_by('-is_default', 'id')

    context = {
        'addresses': addresses,
    }
    return render(request, 'user_profile/address_management.html', context)


def set_as_default(request, address_id):
    address = Address.objects.get(id=address_id)
    old_default = Address.objects.filter(is_default=True)
    for old in old_default:
        old.is_default = False
        old.save()
    address.is_default = True
    address.save()
    addresses = Address.objects.filter(user__id=request.user.id,is_active=True).order_by('-is_default', 'id')
    return render(request, 'user_profile/address_management.html', {'addresses': addresses})


def delete_address(request, address_id):
    current_address = Address.objects.get(id=address_id)
    if current_address.is_default:
        new_address = Address.objects.exclude(id=address_id).filter(is_active=True).first()
        new_address.is_default = True
        new_address.save()
    current_address.is_active = False
    current_address.save()
    addresses = Address.objects.filter(user=request.user,is_active=True).order_by('-is_default', 'id')
    return render(request, 'user_profile/address_management.html', {'addresses': addresses})


def add_address(request):
    if request.method == "POST":
        name = request.POST['name']
        number = request.POST['number']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        district = request.POST['district']
        landmark = request.POST['landmark']
        pincode = request.POST['pincode']
        country = request.POST['country']
        if not re.match(r'^\d{10}$', number):
            messages.error(request, 'Invalid phone number. Phone number must contain 10 digits.')
            return redirect('add_address')

        if number.startswith('0'):
            messages.error(request, 'Invalid phone number. Phone number cannot start with zero.')
            return redirect('add_address')

        if not re.match(r'^\d{6}$', pincode):
            messages.error(request, 'Invalid phone number. Phone number must contain 10 digits.')
            return redirect('add_address')

        if pincode.startswith('0'):
            messages.error(request, 'Invalid phone number. Phone number cannot start with zero.')
            return redirect('add_address')
        firstornot =Address.objects.filter(user=request.user)
        if firstornot.exists():
            address = Address(user=request.user,name=name,mobile=number,address=address,city=city,district=district,landmark=landmark,state=state,pincode=pincode,country=country)
            address.save()
        else:
            address = Address(user=request.user,name=name,mobile=number,address=address,city=city,district=district,landmark=landmark,state=state,pincode=pincode,country=country)
            address.is_default = True
            address.save()
        return redirect('address_management')

    return render(request, 'user_profile/add_address.html')

def edit_address(request,address_id):
    if request.method == "POST":
        addresss = Address.objects.get(id=address_id)
        addresss.name = request.POST['name']
        addresss.mobile = request.POST['number']
        addresss.address = request.POST['address']
        addresss.city = request.POST['city']
        addresss.state = request.POST['state']
        addresss.district = request.POST['district']
        addresss.landmark = request.POST['landmark']
        addresss.pincode = request.POST['pincode']
        addresss.country = request.POST['country']
        addresss.save()

    return render(request,'user_profile/edit_address.html')

def change_password(request):
    if request.method == "POST":
        new = request.POST['new_password1']
        cnew = request.POST['new_password2']
        if new != cnew :
            messages.error(request,"Passwords dont match", extra_tags="danger")
            return redirect('change_password')
        else:
            user = request.user
            user.password = new
            user.save()
            messages.success(request,"Password changed")
            return redirect('user_profile')

        pass
    return render(request,'user_profile/changepassword.html')


def My_Wallet(request):
    mywallet =  Wallet.objects.get(user=request.user)
    balance = mywallet.balance

    transactions= WalletTransaction.objects.filter(wallet=mywallet)


    context={
        'balance':balance,
        'transactions':transactions
    }
    return render(request,'user_profile/Mywallet.html',context)
