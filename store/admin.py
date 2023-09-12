from django.contrib import admin

from store.models import Book, Category,Language,Cover,Variant,Coupon

admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Language)
admin.site.register(Cover)
admin.site.register(Variant)
admin.site.register(Coupon)
# Register your models here.
