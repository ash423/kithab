from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render
import razorpay
from store.models import *

def trialhome(request):
    coupons = Coupon.objects.all()
    categories = Category.objects.all()
    covers = Cover.objects.all()
    languages = Language.objects.all()
    context = {
        'categories':categories,
        'covers' : covers,
        'languages':languages,
        'coupons':coupons
    }

    return render(request,'trialdemo/home.html',context)

def product_list(request, category, slug):
    search = request.GET.get('q')
    sort = request.GET.get('sort')
    heading = slug

    if category == 'Category':
        if slug == 'all':
            books = Book.objects.all()
            heading = 'All Books'
        else:
            books = Book.objects.filter(category__slug=slug)
            heading = Category.objects.get(slug=slug).name
        is_variant = False
    elif category == 'Language':
        language = Language.objects.get(slug=slug)
        books = BookVariant.objects.filter(language=language).distinct('book')
        book_ids = [book.id for book in books]
        books = BookVariant.objects.filter(id__in=book_ids)
        heading = language.name
        is_variant = True
    elif category == 'CoverType':
        cover_type = CoverType.objects.get(slug=slug)
        books = BookVariant.objects.filter(cover_type=cover_type)
        heading = cover_type.name
        is_variant = True

    if search:
        if is_variant:
            books = books.filter(book__name__icontains=search)
        else:
            books = books.filter(name__icontains=search)

    if sort:
        if sort == 'atoz':
            books = books.order_by('book__name') if is_variant else books.order_by('name')
            sort = 'A to Z'
        elif sort == 'discount':
            if is_variant:
                books = books.order_by('-offer_percentage', '-price')
            else:
                subquery = BookVariant.objects.filter(book_id=OuterRef('id')).order_by('id')
                books = books.annotate(first_variant_offer_percentage=Subquery(subquery.values('offer_percentage')[:1]))
                books = books.annotate(first_variant_price=Subquery(subquery.values('price')[:1]))
                books = books.order_by('-first_variant_offer_percentage', '-first_variant_price')
            sort = 'Discount'
        elif sort == 'pricelth':
            if is_variant:
                books = books.order_by('price')
            else:
                subquery = Variant.objects.filter(book_id=OuterRef('id')).order_by('id')
                books = books.annotate(first_variant_price=Subquery(subquery.values('price')[:1]))
                books = books.order_by('first_variant_price')
            sort = 'Price: Low to High'
        elif sort == 'pricehtl':
            if is_variant:
                books = books.order_by('-price')
            else:
                subquery = Variant.objects.filter(book_id=OuterRef('id')).order_by('id')
                books = books.annotate(first_variant_price=Subquery(subquery.values('price')[:1]))
                books = books.order_by('-first_variant_price')
            sort = 'Price: High to Low'
        elif sort == 'newest':
            books = books.order_by('id')
            sort = 'Newest'
        elif sort == 'oldest':
            books = books.order_by('-id')
            sort = 'Oldest'
        else:
            sort = 'Sort by ↑↓'
    else:
        sort = 'Sort by ↑↓'

    paginator = Paginator(books, 6)
    page = request.GET.get('page')
    books = paginator.get_page(page)

    categories = Category.objects.all()
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    wishlist_count = WishlistItem.objects.filter(
        wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']
    languages = Language.objects.all()
    formats = CoverType.objects.all()

    context = {
        'books': books,
        'categories': categories,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'languages': languages,
        'formats': formats,
        'is_variant': is_variant,
        'sort': sort,
        'heading': heading,
    }
    return render(request, 'store/product_list.html', context)

