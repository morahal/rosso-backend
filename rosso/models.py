from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     address = models.CharField(max_length=255, blank=True, null=True)
#     mobile_number = models.CharField(max_length=20, blank=True, null=True)

#     def __str__(self):
#         return self.user.username

# # Signal to create or update the user profile whenever a user instance is saved
# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#     instance.userprofile.save()

# Items Model
class Item(models.Model):
    section = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=30)
    size = models.CharField(max_length=30)
    item_type = models.CharField(max_length=100)
    image1 = models.ImageField(upload_to='item_images/')
    image2 = models.ImageField(upload_to='item_images/')
    image3 = models.ImageField(upload_to='item_images/')
    description = models.TextField()
    remaining_quantity = models.IntegerField()

    def __str__(self):
        return self.name

# Purchases Model
class Purchase(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_date_start = models.DateField()
    delivery_date_end = models.DateField()
    status = models.CharField(max_length=100)

    def __str__(self):
        return f'Purchase {self.id} by {self.customer.username}'

# PurchaseItem Model
class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return self.quantity

# Favorites Model
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'item')

    def __str__(self):
        return f'{self.user.username} - {self.item.name}'

    