from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to='category_images/')
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True)
    def save(self, *args, **kwargs):
        # Generate slug from the name field
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class Book(models.Model):

    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.CharField(max_length=255)
    no_of_pages = models.PositiveSmallIntegerField()
    publisher = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/')
    is_active = models.BooleanField(default='True')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title

class Language(models.Model):
    languages = models.CharField(max_length=255)
    def __str__(self):
        return self.languages


class Cover(models.Model):
    cover = models.CharField(max_length=255)

    def __str__(self):
        return self.cover


class Variant(models.Model):
    book_id = models.ForeignKey(Book,on_delete=models.CASCADE)
    language_variant = models.ForeignKey(Language,on_delete=models.CASCADE)
    cover_type = models.ForeignKey(Cover,on_delete=models.CASCADE)
    price = models.IntegerField()
    stock = models.IntegerField()
    is_active = models.BooleanField(default='True')

    def __str__(self):
        return f"{self.book_id.title} {self.language_variant} {self.cover_type}"

class VariantImages(models.Model):
    image = models.ImageField(upload_to='variant_images/')
    book_variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Variant: {self.book_variant} - Image: {self.image.name}"


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.FloatField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)  # Allow null values
    minimum_order_amount = models.FloatField()
    is_active = models.BooleanField(default=False)
    single_use_per_user = models.BooleanField(default=False)
    quantity = models.IntegerField(default=10)

    def __str__(self):
        return self.code

# Create your models here.
