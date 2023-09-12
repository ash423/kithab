from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from store.models import Variant


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Cart #{self.pk} for {self.user.username}"

    def get_total_price(self):
        return self.cartitem_set.aggregate(total_price=Sum('price'))['total_price']


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.quantity * self.price




class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Wishlist #{self.pk} for {self.user.username}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
