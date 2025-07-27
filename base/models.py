from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import MaxValueValidator

# Create your models here.

class Clothing(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Listing Title + product description
    name = models.CharField(max_length=250)
    details = models.TextField(max_length=1000)

    description = models.TextField(max_length=1000)

    # Nike/Addidas/Puma/ etc.
    brand = models.CharField(max_length=100)

    # shoes/trainers/jogging bottoms
    category = models.CharField(max_length=100) 

    # M for Man, W for Women, C for child
    
    gender = models.CharField(max_length=1) 
    size = models.TextField(max_length=40)

    color = models.CharField(null=True, blank=True, max_length=50)
    price = models.DecimalField(decimal_places=2, max_digits=5)
    rating = models.DecimalField(decimal_places=1, max_digits=2)

    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    class meta:
        ordering = ['-updated', '-created']

    
    def __str__(self):
        return self.name
    

class Review(models.Model):
    #Unique ID for each review
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # user associated with review - user deleted, delete review
    # each user has multiple reviews
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    # Product associated with review - product deleted, delete review
    # each product has multiple reviews
    product_ID = models.ForeignKey(Clothing, on_delete=models.CASCADE)

    # Moderation - allows offensive review deletion
    is_active = models.BooleanField(default=True)

    verified = models.BooleanField()
    
    title = models.CharField(null=False, max_length=50)
    description_review = models.TextField(null=False, max_length=1000)
    stars = models.IntegerField(null=False, validators=[MaxValueValidator(5)])

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


    class meta:
        ordering = ['-updated', '-created']

class Order(models.Model):
    # primary key
    purchase_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # order is associated with each user
    # when user is deleted, order record retained, just set to Null
    user_id = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_intent_id = models.CharField(max_length=255)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    paid = models.BooleanField(default=False)
    paid_time = models.DateTimeField(null=True, blank=True)

    class meta:
        ordering = ['-updated', '-created']

class OrderItem(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # product, purchase the order is associated with 
    purchase = models.ForeignKey(Order, on_delete=models.PROTECT)
    product_id = models.ForeignKey(Clothing, on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField()

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class meta:
        ordering = ['-updated', '-created']

