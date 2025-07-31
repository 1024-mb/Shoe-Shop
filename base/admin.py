from django.contrib import admin
from .models import Clothing, Review, ClothingColor, ProductVariant


# Register your models here.


admin.site.register(Clothing)

admin.site.register(Review)
admin.site.register(ClothingColor)
admin.site.register(ProductVariant)
