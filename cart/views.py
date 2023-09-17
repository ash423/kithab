import re
from datetime import datetime

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404,HttpResponseRedirect
from django.http import HttpResponse, JsonResponse
from decimal import Decimal
from django.shortcuts import render
from django.db.models import Sum, Q, F
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.db.models import Subquery, OuterRef
from cart.models import Cart, CartItem, Wishlist, WishlistItem
from store.models import Variant
from orders.models import *
from userprofile.models import Address,Wallet,WalletTransaction


# Create your views here.

def view_cart(request):
    user = request.user

    if user.is_authenticated:
        cart = Cart.objects.get(user=user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id

    cart_items = cart.cartitem_set.annotate(subtotal=F('quantity') * F('price'))
    subtotal = cart_items.aggregate(subtotal_price=Sum('subtotal'))['subtotal_price'] or Decimal('0.00')
    total_item_count = cart_items.aggregate(total_count=Sum('quantity'))['total_count'] or 0


    Q1 = Q(single_use_per_user=False)
    Q2 = (~Q(single_use_per_user=True) | ~Q(order__user=request.user)) if request.user.is_authenticated else Q()
    Q3 = Q(is_active=True) & Q(valid_from__lte=timezone.now()) & (Q(valid_to__gte=timezone.now()) | Q(valid_to__isnull=True)) & (Q(minimum_order_amount__isnull=True) | Q(minimum_order_amount__lte=subtotal))
    Q4 = Q(quantity__gte=1)
    valid_coupons = Coupon.objects.filter(Q1 | Q2, Q3, Q4)

    # Get the applied coupon from the session or set a default value
    applied_coupon = request.session.get('applied_coupon', {
        'id': None,
        'code': None,
        'discount': '0.00',
    })

    discount_price = Decimal(applied_coupon.get('discount', '0.00'))
    total_price = subtotal - discount_price if discount_price <= subtotal else Decimal('0.00')

    page_number = request.GET.get('page')
    items_per_page = 3
    paginator = Paginator(cart.cartitem_set.all(), items_per_page)
    cart_items = paginator.get_page(page_number)
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'discount_amount': discount_price,
        'total_price': total_price,
        'cart_items': cart_items,
        'valid_coupons': valid_coupons,
        'applied_coupon': applied_coupon,
        'total_item_count':total_item_count,
    }

    return render(request, 'cart/cart.html', context)





def add_to_cart(request, variant_id):


    variant = Variant.objects.get(id=variant_id)
    print(variant.book_id.category.offer_active)
    if variant.book_id.category.offer_active:
        offer = variant.book_id.category.offer
        offer_pricea = (1-(offer/100))*variant.price
        variant.offer_price = offer_pricea
        variant.save()
        print(offer_pricea)
    user = request.user
    if user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create()

    cart_item = cart.cartitem_set.filter(variant=variant).first()    #edited from get or create



    if cart_item:
        available_stock = variant.stock - cart_item.quantity
        requested_quantity = 1
        if requested_quantity <= available_stock:
            cart_item.quantity += requested_quantity
            cart_item.save()
            messages.success(request,'Item added to cart')
        else:
            messages.error(request,'Request quantity exceeds available stock')
    else:
        if 1 <= variant.stock:
            if variant.book_id.category.offer_active:
                CartItem.objects.create(cart=cart,variant=variant,quantity=1,price=variant.offer_price)
            else:
                CartItem.objects.create(cart=cart,variant=variant,quantity=1,price=variant.price)
            messages.success(request,'Item added to cart')
        else:
            messages.error(request,'Requested quantity exceeds available stock')
    if not user.is_authenticated:
        request.session['cart_id'] = cart.id



    return HttpResponseRedirect(request.META['HTTP_REFERER'])


# def update_quantity(request,cart_item_id, num):
#     cart_item = CartItem.objects.get(id=cart_item_id)
#     if num == 1 and cart_item.variant.stock > cart_item.quantity:
#         cart_item.quantity += 1
#     elif num == 0 and cart_item.quantity > 1:
#         cart_item.quantity -= 1
#     cart_item.save()
#     cart = Cart.objects.get_or_create(user=request.user)[0] if request.user.is_authenticated else None
#     if cart:
#         cart_items = cart.cartitem_set.annotate(subtotal=F('quantity') * F('variant__price'))
#         subtotal = cart_items.aggregate(subtotal_price=Sum('subtotal'))['subtotal_price'] or 0
#
#         applied_coupon = request.session.get('applied_coupon', None)
#
#         if applied_coupon:
#             coupon_id = applied_coupon.get('id', None)
#             coupon = Coupon.objects.filter(id=coupon_id, is_active=True).first()
#
#             if coupon and coupon.minimum_order_amount is not None and subtotal < coupon.minimum_order_amount:
#                 # Remove the applied coupon from the session
#                 request.session.pop('applied_coupon', None)
#                 messages.warning(request, "The applied coupon's criteria no longer met. Coupon removed.")
#             elif coupon and coupon.discount > subtotal:
#                 # Remove the applied coupon from the session
#                 request.session.pop('applied_coupon', None)
#                 messages.warning(request, "The applied coupon's discount is greater than the order subtotal. Coupon removed.")
#
#
#     return redirect('view_cart')

def update_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity'))

        cart_item = CartItem.objects.get(id=item_id)
        variant = cart_item.variant
        available_stock = variant.stock - cart_item.quantity

        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than zero.')
        elif quantity <= available_stock + cart_item.quantity:
            cart_item.quantity = quantity
            cart_item.save()

            # Update the quantity in the session for non-authenticated users
            if not request.user.is_authenticated:
                cart_session = request.session.get('cart', {})
                cart_session[item_id] = quantity
                request.session['cart'] = cart_session

            # Check if the cart's subtotal meets the minimum requirement for the applied coupon (if any)
            cart = Cart.objects.get_or_create(user_id=request.user)[0] if request.user.is_authenticated else None
            if cart:

                cart_items = cart.cartitem_set.annotate(subtotal=F('quantity') * F('variant__price'))
                if variant.book_id.category.offer_active:
                    cart_items = cart.cartitem_set.annotate(subtotal=F('quantity') * F('variant__offer_price'))

                subtotal = cart_items.aggregate(subtotal_price=Sum('subtotal'))['subtotal_price'] or 0

                applied_coupon = request.session.get('applied_coupon', None)

                if applied_coupon:
                    coupon_id = applied_coupon.get('id', None)
                    coupon = Coupon.objects.filter(id=coupon_id, is_active=True).first()

                    if coupon and coupon.minimum_order_amount is not None and subtotal < coupon.minimum_order_amount:
                        # Remove the applied coupon from the session
                        request.session.pop('applied_coupon', None)
                        messages.warning(request, "The applied coupon's criteria no longer met. Coupon removed.")
                    elif coupon and coupon.discount > subtotal:
                        # Remove the applied coupon from the session
                        request.session.pop('applied_coupon', None)
                        messages.warning(request, "The applied coupon's discount is greater than the order subtotal. Coupon removed.")

            return JsonResponse({'success': True, 'stock': variant.stock})

        else:
            messages.error(request, 'Requested quantity exceeds available stock.')

    return JsonResponse({'success': False})


def remove_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()
    messages.success(request,'Item removed from cart')
    try:
        cart = Cart.objects.get_or_create(user_id=request.user)[0] if request.user.is_authenticated else None


        if cart :
            cart_items = cart.cartitem_set.annotate(subtotal=F('quantity') * F('variant__price'))
            subtotal = cart_items.aggregate(subtotal_price=Sum('subtotal'))['subtotal_price'] or 0

            applied_coupon = request.session.get('applied_coupon', None)

            if applied_coupon:
                coupon_id = applied_coupon.get('id', None)
                coupon = Coupon.objects.filter(id=coupon_id, is_active=True).first()

                if coupon and coupon.minimum_order_amount is not None and subtotal < coupon.minimum_order_amount:
                    # Remove the applied coupon from the session
                    request.session.pop('applied_coupon', None)
                    messages.warning(request, "The applied coupon's criteria no longer met. Coupon removed.")
                elif coupon and coupon.discount > subtotal:
                    # Remove the applied coupon from the session
                    request.session.pop('applied_coupon', None)
                    messages.warning(request, "The applied coupon's discount is greater than the order subtotal. Coupon removed.")
    except :
        pass

    return redirect('view_cart')

def apply_coupon(request):
    if request.method == 'POST':
        coupon_id = request.POST.get('coupon_id')
        try:
            coupon_id = int(coupon_id)
            coupon = get_object_or_404(Coupon, id=coupon_id)
            discount = coupon.discount
            request.session['applied_coupon'] = {
                'id': coupon.id,
                'code': coupon.code,
                'discount': discount,
            }

            cart = Cart.objects.get(user_id=request.user)
            cart_items = cart.cartitem_set.annotate(subtotal=F('quantity') * F('variant__price'))
            subtotal = cart_items.aggregate(subtotal_price=Sum('subtotal'))['subtotal_price'] or Decimal('0.00')

            discount_amount = Decimal(discount)
            total_price = subtotal  - discount_amount

            if total_price < coupon.minimum_order_amount:
                request.session.pop('applied_coupon', None)
                messages.warning(request, f"The coupon '{coupon.code}' requires a minimum total of '{coupon.discount}'. Coupon removed.")
            else:
                messages.success(request, f"Coupon '{coupon.code}' applied successfully!")

        except (ValueError, TypeError, Coupon.DoesNotExist):
            # Remove the applied coupon from the session
            request.session.pop('applied_coupon', None)
            messages.error(request, "Invalid coupon. Coupon not applied.")

    return redirect('view_cart')








def wishlist_summary(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.wishlistitem_set.all().order_by('variant')


    if not wishlist_items.exists():
        return render(request,'cart/empty_wishlist.html')

    paginator = Paginator(wishlist_items, 7)
    page = request.GET.get('page')
    wishlist_items = paginator.get_page(page)

    context = {
        'wishlist_items': wishlist_items,

    }
    return render(request, 'cart/wishlist.html', context)
    # except:
    #     return render(request, 'cart/empty_wishlist.html')


def add_to_wishlist(request, variant_id):
    variant = Variant.objects.get(id=variant_id)
    user = request.user
    wishlist, created = Wishlist.objects.get_or_create(user=user)

    try:
        wishlist_item = WishlistItem.objects.get(wishlist=wishlist, variant=variant)
    except:
        wishlist_item = WishlistItem.objects.create(wishlist=wishlist, variant=variant)
    wishlist_item.save()

    return redirect('wishlist_summary')


def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = WishlistItem.objects.get(id=wishlist_item_id)
    wishlist_item.delete()


    return redirect('wishlist_summary')


def wishlist_to_cart(request, wishlist_item_id):
    wishlist_item = WishlistItem.objects.get(id=wishlist_item_id)
    variant_id = wishlist_item.variant.id
    wishlist_item.delete()

    return redirect('add_to_cart', variant_id)

@login_required(login_url='signin')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def checkout(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = cart.cartitem_set.all()
    user_wallet, created = Wallet.objects.get_or_create(user=user)
    for item in cart_items:
        print(item.variant.stock)

    if not cart_items:
        return redirect('home')


    out_of_stock_products = [f"{item.variant.book_id.title} - {item.variant}" for item in cart_items if
                             item.variant.stock <= item.quantity ]
    if out_of_stock_products:

        error_message = ", ".join(out_of_stock_products) + " is/are out of stock. Please remove them from your cart."
        messages.error(request, error_message)
        return redirect('view_cart')

    subtotal = cart_items.aggregate(subtotal=Sum(F('quantity') * F('variant__price')))['subtotal'] or Decimal('0.00')
    shipping_charge = Decimal('50') if subtotal < Decimal('1000') else Decimal('0.00')

    applied_coupon = request.session.get('applied_coupon', {'discount': '0.00'})
    discount_amount = Decimal(applied_coupon.get('discount', '0.00'))

    # Calculate the total_price directly without using the session
    total_price = subtotal - discount_amount

    addresses = Address.objects.filter(user=user,is_active=True)

    context = {
        'cart': cart,
        'subtotal': subtotal,

        'discount_amount': discount_amount,
        'total_price': total_price,
        'cart_items': cart_items,
        'addresses': addresses,
        'wallet_amount': user_wallet.balance,
    }

    return render(request, 'cart/checkout.html', context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def order_placed(request,addressid):
    print("Order Placed")
    user_address = get_object_or_404(Address, id=addressid, user=request.user)
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    if cart_items:
        subtotal = cart_items.aggregate(subtotal=Sum(F('quantity') * F('variant__price')))['subtotal'] or Decimal('0.00')
        applied_coupon_id = request.session.get('applied_coupon', {}).get('id')
        discount_amount = Decimal('0.00')
        coupon = None

        if applied_coupon_id is not None:
            try:
                coupon = get_object_or_404(Coupon, id=applied_coupon_id)
                discount_amount = Decimal(coupon.discount)
            except Coupon.DoesNotExist:
                coupon = None

            # Calculate the total price based on the discount amount
        total_price = subtotal  - discount_amount



        order = Order.objects.create(
                user=request.user,
                address=user_address,
                payment_status='Cash on Delivery',
                payment_method='Cash on Delivery',
                order_status='Processing',
                price=subtotal,
                coupon = coupon,
                discount= discount_amount,
                price_after_discount= total_price

            )

        for cart_item in cart_items:
            OrderItem.objects.create(
                    order=order,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=cart_item.price

                )
            variant = cart_item.variant
            variant.stock -= cart_item.quantity
            variant.save()
        if coupon:
            if coupon.quantity >= 1:
                coupon.quantity -= 1
                coupon.save()
        cart_items.delete()
        orderId = order.id
        request.session.pop('applied_coupon', None)
    return render(request, 'cart/order_placed.html')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def pay_using_wallet(request,addressid):
    if request.method == 'POST':
        payment_id = request.POST.getlist('payment_id')[0]
        orderId = request.POST.getlist('orderId')[0]
        signature = request.POST.getlist('signature')[0]
        user_address = get_object_or_404(Address, id=addressid, user=request.user)
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.all()
        if cart_items:
            subtotal = cart_items.aggregate(subtotal=Sum(F('quantity') * F('variant__price')))['subtotal'] or Decimal('0.00')

            applied_coupon_id = request.session.get('applied_coupon', {}).get('id')

            discount_amount = Decimal('0.00')
            coupon = None

            # If an applied_coupon_id exists, attempt to retrieve the coupon
            if applied_coupon_id is not None:
                try:
                    coupon = get_object_or_404(Coupon, id=applied_coupon_id)
                    discount_amount = Decimal(coupon.discount)
                except Coupon.DoesNotExist:
                    # Handle the case when the coupon with the stored ID no longer exists
                    coupon = None

            # Calculate the total price based on the discount amount
            total_price = subtotal  - discount_amount



            order = Order.objects.create(
                user=request.user,
                address=user_address,
                payment_status='Paid',
                payment_method='Wallet',
                order_status='Processing',
                price=subtotal,
                coupon = coupon,
                discount= discount_amount,
                price_after_discount= total_price

            )
            user_wallet, created = Wallet.objects.get_or_create(user=request.user)
            user_wallet -= total_price
            user_wallet.save()

            WalletTransaction.objects.create(
                wallet=user_wallet,
                amount=total_price,
                transaction_type='Credit',
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=cart_item.price

                )
                variant = cart_item.variant
                variant.stock -= cart_item.quantity
                variant.save()
            if coupon:
                if coupon.quantity >= 1:
                    coupon.quantity -= 1
                    coupon.save()
            cart_items.delete()
            orderId = order.id
            request.session.pop('applied_coupon', None)
    return render(request, 'cart/order_placed.html')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def orderplaced(request):
    return render(request, 'cart/order_placed.html')

def initiate_payment(request):

    if request.method == 'POST':
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = cart.cartitem_set.all()
        user_wallet, created = Wallet.objects.get_or_create(user=user)
        if not cart_items:
            return redirect('home')
        subtotal = cart_items.aggregate(subtotal=Sum(F('quantity') * F('variant__price')))['subtotal'] or Decimal('0.00')


        applied_coupon = request.session.get('applied_coupon', {'discount': '0.00'})
        discount_amount = Decimal(applied_coupon.get('discount', '0.00'))


        total_price = subtotal - discount_amount


    # Retrieve the total price and other details from the backend
        # cart = Cart.objects.get(user_id=request.user)
        # cart_items = cart.cartitems_set.all()



        total_amount_in_cents = int(total_price*100)


        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        payment = client.order.create({

            'amount': total_amount_in_cents,
            'currency': 'INR',
            'payment_capture': 1

        })

        response_data = {
            'order_id': payment['id'],
            'amount': payment['amount'],
            'currency': payment['currency'],
            'key': settings.RAZOR_KEY_ID,

        }
        return JsonResponse(response_data)

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request method'})


def online_payment_order(request, add_id):
    if request.method == 'POST':
        payment_id = request.POST.getlist('payment_id')[0]
        orderId = request.POST.getlist('orderId')[0]
        signature = request.POST.getlist('signature')[0]
        user_address = get_object_or_404(Address, id=add_id, user=request.user)
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.all()
        if cart_items:
            subtotal = cart_items.aggregate(subtotal=Sum(F('quantity') * F('variant__price')))['subtotal'] or Decimal('0.00')

            applied_coupon_id = request.session.get('applied_coupon', {}).get('id')

            discount_amount = Decimal('0.00')
            coupon = None

            # If an applied_coupon_id exists, attempt to retrieve the coupon
            if applied_coupon_id is not None:
                try:
                    coupon = get_object_or_404(Coupon, id=applied_coupon_id)
                    discount_amount = Decimal(coupon.discount)
                except Coupon.DoesNotExist:
                    # Handle the case when the coupon with the stored ID no longer exists
                    coupon = None

            # Calculate the total price based on the discount amount
            total_price = subtotal  - discount_amount



            order = Order.objects.create(
                user=request.user,
                address=user_address,
                payment_status='Paid',
                payment_method='Prepaid',
                order_status='Processing',
                price=subtotal,
                razor_pay_payment_id=payment_id,
                razor_pay_payment_signature=signature,
                razor_pay_order_id=orderId,
                coupon = coupon,
                discount= discount_amount,
                price_after_discount= total_price

            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=cart_item.price

                )
                variant = cart_item.variant
                variant.stock -= cart_item.quantity
                variant.save()
            if coupon:
                if coupon.quantity >= 1:
                    coupon.quantity -= 1
                    coupon.save()
            cart_items.delete()
            orderId = order.id
            request.session.pop('applied_coupon', None)


            return JsonResponse({'message': 'Order placed successfully', 'orderId': orderId})
    else:
        return JsonResponse({'error': 'Invalid request method'})

def addaddress_checkout(request):
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
            return redirect('addaddress_checkout')

        if number.startswith('0'):
            messages.error(request, 'Invalid phone number. Phone number cannot start with zero.')
            return redirect('addaddress_checkout')

        if not re.match(r'^\d{6}$', pincode):
            messages.error(request, 'Invalid phone number. Phone number must contain 10 digits.')
            return redirect('addaddress_checkout')

        if pincode.startswith('0'):
            messages.error(request, 'Invalid phone number. Phone number cannot start with zero.')
            return redirect('addaddress_checkout')

        firstornot =Address.objects.filter(user=request.user)
        if firstornot.exists():
            address = Address(user=request.user,name=name,mobile=number,address=address,city=city,district=district,landmark=landmark,state=state,pincode=pincode,country=country)
            address.save()
        else:
            address = Address(user=request.user,name=name,mobile=number,address=address,city=city,district=district,landmark=landmark,state=state,pincode=pincode,country=country)
            address.is_default = True
            address.save()
        return redirect('checkout')

    return render(request, 'cart/addaddress_checkout.html')

def remove_coupon(request):
    # Remove the applied coupon from the session
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        messages.success(request, "Coupon removed successfully!")
    else:
        messages.warning(request, "No coupon applied.")

    # Get the URL of the previous page and redirect
    previous_page = request.META.get('HTTP_REFERER', None)
    return redirect(previous_page) if previous_page else redirect('view_cart')