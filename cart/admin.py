from django.contrib import admin
from cart.models import Wishlist,WishlistItem,CartItem,Cart

admin.site.register(Wishlist)
admin.site.register(WishlistItem)
admin.site.register(Cart)
admin.site.register(CartItem)
# Register your models here.
