from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Clothing(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Listing Title + product description
    name = models.CharField(max_length=50)
    desc = models.TextField(max_length=1000)

    # Nike/Addidas/Puma/ etc.
    brand = models.CharField(max_length=30)

    # shoes/trainers/jogging bottoms
    category = models.CharField(max_length=30) 

    # M for Man, W for Women, C for child
    gender = models.CharField(max_length=1) 
    size = models.TextField(max_length=40)

    price = models.DecimalField(decimal_places=2, max_digits=5)
    rating = models.DecimalField(decimal_places=1, max_digits=2)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return self.name
    

class Review(models.Model):
    #Unique ID for each review
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # user associated with review - user deleted, delete review
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    # Product associated with review - product deleted, delete review
    product_ID = models.ForeignKey(Clothing, on_delete=models.CASCADE)


    description_review = models.TextField(null=False, max_length=80)
    stars = models.IntegerField(null=False)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description_review[0:50]


    
