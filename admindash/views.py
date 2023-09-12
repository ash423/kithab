import json
from datetime import timedelta, datetime
from decimal import Decimal

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.core.paginator import Paginator


# Create your views here.
from django.utils import timezone
from django.utils.timezone import make_aware, now

from orders.models import Order,OrderItem
from store.models import Book, Category,Coupon,Variant,Language,Cover



# def admindash(request):
#
#     if request.user.is_superuser:
#         return render(request, 'admin_side/ttt.html')
#     else:
#         return redirect('home')

def admindash(request, date=None):
    if request.user.is_superuser:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if not start_date_str or not end_date_str:
            # Default to last 30 days if no date range provided
            first_order = Order.objects.all().first()
            start_date = first_order.order_date.date() if first_order else date.today()
            end_date = now()
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.min.time()) + timedelta(days=1)

        # Calculate the number of 3-day intervals between start_date and end_date
        num_intervals = (end_datetime - start_datetime).days // 3 + 1
        # Generate the date_range based on the calculated number of intervals
        date_range = [start_datetime + timedelta(days=3 * i) for i in range(num_intervals)]
        sales_data = []

        for date in date_range:
            # Calculate the end of the 3-day interval
            interval_end = date + timedelta(days=2)

            total_sales = Order.objects.filter(
                order_date__range=[date, interval_end],  # Use range filter for the interval
            ).aggregate(total_sales=Sum('price'))['total_sales'] or Decimal('0.00')

            sales_data.append(float(total_sales))  # Convert Decimal to float

        # Serialize data
        serialized_date_range = json.dumps([date.strftime('%Y-%m-%d') for date in date_range])
        serialized_sales_data = json.dumps(sales_data)

        today = date.today()
        today_sales = Order.objects.filter(
            order_date__date=today,
        ).aggregate(total_sales=Sum('price'))['total_sales'] or Decimal('0.00')

        total_sales = Order.objects.filter(payment_status='PAID').aggregate(total_sales=Sum('price'))['total_sales'] or Decimal('0.00')

        # Calculate today's orders
        today = date.today()
        today_orders = Order.objects.filter(order_date__date=today).count()

        # Calculate total orders
        total_orders = Order.objects.count()

        categories = Category.objects.all()
        data = []
        for category in categories:
            product_count = Book.objects.filter(category=category).count()
            data.append(product_count)

        recent_orders = Order.objects.all().order_by('-id')[:8]

        context = {
            'date_range': serialized_date_range,
            'sales_data': serialized_sales_data,
            'today_sales': float(today_sales),
            'total_sales': float(total_sales),
            'today_orders': today_orders,
            'total_orders': total_orders,
            'categories': categories,
            'data': data,
            'recent_orders': recent_orders,
        }

        return render(request, 'admin_side/ttt.html', context)


def userslist(request):
    if request.user.is_superuser:
        users = User.objects.all().order_by('id')
        paginator = Paginator(users, 7)
        page = request.GET.get('page')
        users = paginator.get_page(page)
        context={
      'users':users
   }
        return render(request, 'admin_side/userslist.html',context)
    else:
        return('home')

def block_user(request,user_id):
    if request.user.is_superuser:
        user=User.objects.get(id=user_id)
        user.is_active = False
        user.save()
        return redirect('userslist')
    else:
        print(request.user.is_superuser)
        return redirect('home')

def unblock_user(request,user_id):
    if request.user.is_superuser:
        user=User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        return redirect('userslist')
    else:
        return redirect('home')

def adminsignout(request):
    logout(request)
    return redirect('home')

def productslist(request):
    books = Book.objects.all()

    paginator = Paginator(books, 7)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    context ={
        'books':books
    }
    return render(request,'admin_side/productslist.html',context)


def variants_list(request):
    variants = Variant.objects.all().order_by('id')

    paginator = Paginator(variants, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin_side/variants_list.html', {'variants': page_obj})


def add_variant(request):
    if request.method == "POST":
        book_id = request.POST['product']
        book=Book.objects.get(id=book_id)
        lan_id = request.POST['lang']
        lang =Language.objects.get(id=lan_id)
        cov_id = request.POST('cov')
        cov =Cover.objects.get(id=cov_id)
        price = request.POST['id_price']
        stock = request.POST['id_stock']
        variant = Variant(book_id=book,language_variant=lang,cover_type=cov,price=price,stock=stock)
        variant.save()





    books = Book.objects.all()
    languages = Language.objects.all()
    covers =Cover.objects.all()
    context ={
        'books' : books,
        'languages': languages,
        'covers' : covers,
    }

    return render(request,'admin_side/add_variant.html',context)


def edit_variant(request,variant_id):
    variant = Variant.objects.get(id=variant_id)
    if request.method == "POST":
        price = request.POST['id_price']
        stock = request.POST['id_stock']
        variant.price = price
        variant.stock = stock
        variant.save()
        return redirect('variant_list')


    context = {
        'book' : variant.book_id,
        'language':variant.language_variant,
        'cover':variant.cover_type,
        'price':variant.price,
        'stock':variant.stock

    }
    return render(request,'admin_side/edit_variant.html',context)

def disable_variant(request,variant_id):
    variant = Variant.objects.get(id=variant_id)
    variant.is_active = False
    variant.save()
    return redirect('variants_list')

def enable_variant(request,variant_id):
    variant = Variant.objects.get(id=variant_id)
    variant.is_active = True
    variant.save()
    return redirect('variants_list')


def categorieslist(request):
    categories =Category.objects.all()

    paginator = Paginator(categories, 7)
    page = request.GET.get('page')
    categories = paginator.get_page(page)
    context = {
        'categories':categories
    }
    return render(request,'admin_side/categories_list.html',context)

def addcategory(request):
    if request.method == "POST":
        name = request.POST['cname']
        img = request.FILES.get('img')
        desc = request.POST['desc']


        category = Category(name=name,description=desc)
        if img:
            category.image.save(img.name, img)
        category.save()
        return redirect('categorieslist')
    return render(request,"admin_side/addcategory.html")

def editcategory(request,category_id):

    if request.method == "POST":
        name = request.POST['cname']
        img = request.FILES.get('img')
        desc = request.POST['desc']

        cat = Category.objects.get(id=category_id)
        cat.name=name
        if img:
            cat.image.save(img.name, img)
        cat.description =desc
        cat.save()
        return redirect('categorieslist')
    category = Category.objects.get(id=category_id)
    context = {
        'category':category
    }

    return render(request,"admin_side/editcategory.html",context)

def block_product(request,book_id):
        book=Book.objects.get(id=book_id)
        book.is_active = False
        book.save()
        return redirect('productslist')

def unblock_product(request,book_id):
        book=Book.objects.get(id=book_id)
        book.is_active = True
        book.save()
        return redirect('productslist')

def addproduct(request):
    if request.method == "POST":
        title = request.POST['atitle']
        img = request.FILES.get('img')
        desc = request.POST['desc']
        num =  request.POST.get('num')
        author = request.POST['author']
        publisher = request.POST['publisher']
        categor = request.POST['cat']
        cc =Category.objects.get(id=categor)

        product = Book(title=title,category=cc,author=author,no_of_pages=num,publisher=publisher,description=desc)
        if img:
            product.cover_image.save(img.name, img)
        product.save()

        return redirect('productslist')

    category = Category.objects.all()
    context ={
        'categories':category
    }
    return render(request,'admin_side/addproducts.html',context)

def editproduct(request,book_id):
    if request.method == "POST":
        title = request.POST['atitle']
        img = request.FILES.get('img')
        desc = request.POST['desc']
        num =  request.POST.get('num')
        author = request.POST['author']
        publisher = request.POST['publisher']
        categor = request.POST['cat']

        product = Book.objects.get(id=book_id)
        product.title = title
        product.category = Category.objects.get(id=categor)
        product.author = author
        product.no_of_pages = num
        product.publisher = publisher
        product.description = desc

        if img:
            product.cover_image.save(img.name, img)
        product.save()
        return redirect('productslist')

    book = Book.objects.get(id=book_id)
    context={
        'book' : book
    }
    return render(request,'admin_side/editproduct.html',context)

def orderslist(request):
    orders = Order.objects.exclude(Q(price=0) | Q(price=1)).order_by('-order_date')

    paginator = Paginator(orders, 7)
    page = request.GET.get('page')
    orders = paginator.get_page(page)


    context = {
        'orders':orders,
    }
    return render(request,'admin_side/orderlist.html',context)

def change_order_status(request,orderid,statusid):
    ord = Order.objects.get(id=orderid)
    if statusid==1:
        ord.order_status ='Cancelled'
    if statusid==2:
        ord.order_status ='Delivered'
    if statusid==3:
        ord.order_status ='Out for Delivery'
    if statusid == 4:
        ord.order_status = 'Shipped'
    if statusid == 5:
        ord.order_status = 'Returned'
    if statusid == 6:
        ord.order_status = 'Processing'
    ord.save()

    return redirect('orderslist')


def view_coupons(request):

    coupons = Coupon.objects.all()
    paginator = Paginator(coupons, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin_side/couponslist.html', {'coupons': page_obj})


def addcoupon(request):
    if request.method == 'POST':
        code = request.POST.get('code').upper()
        discount = request.POST.get('discount')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        minimum_order_amount = request.POST.get('minimum_order_amount')
        is_active = 'is_active' in request.POST
        single_use_per_user = 'single_use_per_user' in request.POST
        quantity = request.POST.get('quantity')

        if not code or not discount or not valid_from or not quantity:
            return render(request, 'admin_side/addcoupon.html', {'error': 'All fields are required.'})

        try:
            discount = float(discount)
            valid_from = make_aware(timezone.datetime.strptime(valid_from, '%Y-%m-%d'))
            valid_to = make_aware(timezone.datetime.strptime(valid_to, '%Y-%m-%d')) if valid_to else None
            quantity = int(quantity)
        except (ValueError, TypeError):
            return render(request, 'admin_side/addcoupon.html', {'error': 'Invalid data format.'})

        now = timezone.now()
        if  (valid_to and valid_to < now):
            return render(request, 'admin_side/addcoupon.html', {'error': 'Valid from and valid to dates must be in the future.'})

        if valid_to and valid_from >= valid_to:
            return render(request, 'admin_side/addcoupon.html', {'error': 'Valid from date must be before valid to date.'})

        if Coupon.objects.filter(code=code).exists():
            return render(request, 'admin_side/addcoupon.html', {'error': 'Coupon code already exists.'})

        new_coupon = Coupon(
            code=code,
            discount=discount,
            valid_from=valid_from,
            minimum_order_amount=minimum_order_amount,
            is_active=is_active,
            single_use_per_user=single_use_per_user,
            quantity=quantity,
        )

        if valid_to:
            new_coupon.valid_to = valid_to

        try:
            new_coupon.save()
        except IntegrityError as e:
            print("Error:", e)
            return render(request, 'add_coupon.html', {'error': 'Error saving the coupon. Please try again.'})

        return redirect('view_coupon')
    return render(request, 'admin_side/addcoupon.html')



def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        discount = request.POST.get('discount')
        valid_to = request.POST.get('valid_to')
        minimum_order_amount = request.POST.get('minimum_order_amount')
        quantity = request.POST.get('quantity')

        try:
            discount = float(discount)
            valid_to = make_aware(timezone.datetime.strptime(valid_to, '%Y-%m-%d')) if valid_to else None
            minimum_order_amount = float(minimum_order_amount)
            quantity = int(quantity)
        except (ValueError, TypeError):
            return render(request, 'admin_side/editcoupon.html', {'error': 'Invalid data format.', 'coupon': coupon})

        now = timezone.now()
        if valid_to and valid_to < now:
            return render(request, 'admin_side/editcoupon.html', {'error': 'Valid to date must be in the future.', 'coupon': coupon})

        coupon.discount = discount
        coupon.valid_to = valid_to
        coupon.minimum_order_amount = minimum_order_amount
        coupon.quantity = quantity

        coupon.save()
        return redirect('view_coupon')

    return render(request, 'admin_side/editcoupon.html', {'coupon': coupon})


def enable_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    coupon.is_active = True
    coupon.save()
    return redirect('view_coupon')

def disable_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    coupon.is_active = False
    coupon.save()
    return redirect('view_coupon')

def sales_report(request):
    if request.user.is_superuser:
        # Get the current date and time
        current_datetime = timezone.now()

        # Monthly Sales Report
        monthly_sales = Order.objects.filter(order_date__year=current_datetime.year).values(
            'order_date__month').annotate(total_sales=Sum('price'))

        # Weekly Sales Report
        week_start_date = current_datetime - timedelta(days=current_datetime.weekday())
        week_end_date = week_start_date + timedelta(days=6)
        weekly_sales = Order.objects.filter(order_date__range=[week_start_date, week_end_date]).aggregate(
            total_sales=Sum('price'))

        # Top Selling Products
        top_selling_products = OrderItem.objects.values('variant__book_id__title').annotate(total_sales=Sum('price')).order_by(
            '-total_sales')[:5]

        # Daily Sales for the last 7 days
        daily_sales = Order.objects.filter(order_date__date__gte=current_datetime.date() - timedelta(days=7)).values(
            'order_date__date').annotate(total_sales=Sum('price'))

        # Number of orders in the last 7 days
        orders_last_7_days = Order.objects.filter(
            order_date__date__gte=current_datetime.date() - timedelta(days=7)).count()

        # Number of orders in the last one month
        orders_last_30_days = Order.objects.filter(
            order_date__date__gte=current_datetime.date() - timedelta(days=30)).count()

        # Number of pending orders for today
        pending_orders_today = Order.objects.filter(order_date__date=current_datetime.date(),
                                                    payment_status='PENDING').count()

        # Number of delivered orders for today
        delivered_orders_today = Order.objects.filter(order_date__date=current_datetime.date(),
                                                      order_status='DELIVERED').count()

        context = {
            'monthly_sales': monthly_sales,
            'weekly_sales': weekly_sales,
            'top_selling_products': top_selling_products,
            'daily_sales': daily_sales,
            'orders_last_7_days': orders_last_7_days,
            'orders_last_30_days': orders_last_30_days,
            'pending_orders_today': pending_orders_today,
            'delivered_orders_today': delivered_orders_today,
        }

        return render(request, 'admin_side/sales_report.html', context)