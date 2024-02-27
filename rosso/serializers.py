from rest_framework import serializers
from .models import Item, Purchase, PurchaseItem, Favorite, UserProfile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        # Exclude sensitive information like passwords
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['address', 'phoneNb']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id','section', 'category', 'name', 'price', 'color', 'size', 'item_type', 'image1', 'image2', 'image3', 'description', 'remaining_quantity']

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['id','customer', 'total_price', 'delivery_date_start', 'delivery_date_end', 'status']

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = ['id','purchase', 'item', 'quantity']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id','user', 'item']
