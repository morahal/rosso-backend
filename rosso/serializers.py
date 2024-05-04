from rest_framework import serializers
from .models import Item, Purchase, PurchaseItem, Favorite, UserProfile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        # Exclude sensitive information like passwords
        
# class UserProfileSerializer(serializers.ModelSerializer):

#     user = serializers.SerializerMethodField()

#     class Meta:
#         model = UserProfile
#         fields = ['user','address', 'phoneNb']

#     def get_user(self, obj):
#         user = obj.user
#         return UserSerializer(user).data


# class UserProfileSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

#     class Meta:
#         model = UserProfile
#         fields = ('user', 'address', 'phoneNb')

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    
    class Meta:
        model = UserProfile
        fields = ('email', 'first_name', 'last_name', 'address', 'phoneNb')

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id','section', 'category', 'name', 'price', 'color', 'size', 'item_type', 'image1', 'image2', 'image3', 'description', 'remaining_quantity']


class PurchaseItemSerializer(serializers.ModelSerializer):    
    class Meta:
        model = PurchaseItem
        fields = ['id','purchase', 'item', 'quantity']

class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(source='purchaseitem_set', many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = ['id','customer', 'total_price', 'delivery_date_start', 'delivery_date_end', 'status', 'items']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id','user', 'item']
