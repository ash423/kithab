from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.db.models import Q
from store.models import *


def shop(request,category_id):
    if category_id == 0:
        books =Book.objects.all()
        if request.method == 'POST':
            search = request.POST['search']
            books = books.filter(title__icontains=search)
    else:
       books = Book.objects.filter(category__id=category_id)
    categories = Category.objects.all()
    languages = Language.objects.all()
    covers = Cover.objects.all()
    paginator = Paginator(books, 7)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    context = {
        'num' : 0,
        'books' : books,
        'categories':categories,
        'languages' : languages,
        'covers' : covers
    }
    return render(request,"book_store/shop.html",context)

def search(request):
    search = request.POST['search']
    books = Book.objects.filter(title__icontains=search)
    categories = Category.objects.all()
    languages = Language.objects.all()
    covers = Cover.objects.all()

    paginator = Paginator(books, 7)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    context = {
        'num' : 0,
        'books' : books,
        'categories':categories,
        'languages' : languages,
        'covers' : covers
    }
    return render(request,"book_store/shop.html",context)

def sort(request,sort_id):
    num = 0
    if sort_id == 1:
        books = Book.objects.all().order_by('title')
    if sort_id == 2:
        num=1
        books = Variant.objects.all().order_by('-price')

    if sort_id == 3:
        num=1
        books = Variant.objects.all().order_by('price')

    categories = Category.objects.all()
    languages = Language.objects.all()
    covers = Cover.objects.all()


    paginator = Paginator(books, 7)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    context = {
        'num' : num,
        'books' : books,
        'categories':categories,
        'languages' : languages,
        'covers' : covers
    }
    return render(request,"book_store/shop.html",context)


def applyfilter(request):
    # search
    genreso = request.POST.getlist('genres', [])
    languageso = request.POST.getlist('languages',[])
    coverso = request.POST.getlist('covers',[])
    genres = [int(num) for num in genreso]
    languages = [int(num) for num in languageso]
    covers = [int(num) for num in coverso]
    num = 1
    books = Variant.objects.all()
    print(genres)
    print(languages)
    if genres:
        books = books.filter(book_id__category__id__in=genres)
    if genres and not languages and not covers:
        books = Book.objects.filter(category__id__in=genres)
        num =0

    if languages:
        books = books.filter(language_variant__id__in=languages)
        num = 1

    if covers:
        books = books.filter(cover_type__id__in=covers)
        num = 1


    books =books.order_by('id')
    paginator = Paginator(books, 7)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    categories = Category.objects.all()
    languages = Language.objects.all()
    covers = Cover.objects.all()

    context = {
        'num' : num,
        'books' : books,
        'categories':categories,
        'languages' : languages,
        'covers' : covers
    }
    return render(request,"book_store/shop.html",context)

def trial(request):
    return render(request,"book_store/trial.html")
# Create your views here.

def home(request):
    categories = Category.objects.all
    context = {
        'categories':categories
    }
    return render(request,"book_store/landingpage.html",context)

def product_details(request, book_id, variantid):
    book = Book.objects.get(id=book_id)
    if variantid == 0:
        varian = book.variant_set.all().first()
    else:
        varian = Variant.objects.get(id=variantid)

    Instock = varian.stock

    language = varian.language_variant
    cover_type_variants =book.variant_set.filter(language_variant=language)
    language_variants = book.variant_set.select_related('language_variant').distinct('language_variant')
    price = varian.price
    offer_price = 0

    if varian.book_id.category.offer_active:
        offer = varian.book_id.category.offer
        offer_price = (1-(offer/100))*varian.price
    context = {
        'book': book,
        'variant': varian,
        'cover_type_variants': cover_type_variants,
        'language_variants': language_variants,
        'price': price,
        'Instock': Instock,
        'offer_price': offer_price
    }
    return render(request, "book_store/productdetails.html",context)