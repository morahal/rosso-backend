from decimal import Decimal
from .serializers import  ItemSerializer, PurchaseSerializer, PurchaseItemSerializer, FavoriteSerializer, UserSerializer, UserProfileSerializer,UserProfile
from .models import Item, Purchase, PurchaseItem, Favorite
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from random import randint
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


@api_view(['POST'])
def login_view(request):
    # Get the username and password from the request
    username = request.data.get('username')
    password = request.data.get('password')

    # Authenticate the user
    user = authenticate(request, username=username, password=password)

    if user is not None:
        # The credentials are valid
        login(request, user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            "message": "You're logged in."
        })
    else:
        # The credentials are invalid
        return Response({"message": "Invalid login details."})
    

@api_view(['POST'])
def logout_view(request):
    try:
        # Blacklist the user's token
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()

        # Django logout
        logout(request)

        return Response({"message": "You've been logged out."})
    except Exception as e:
        return Response({"message": "There was an error during logout: {}".format(str(e))})



@api_view(['GET'])  # Or use POST if you prefer
def check_username_exists(request, username):
    """
    Check if a username exists in the database.
    """
    if User.objects.filter(username=username).exists():
        return Response({'message': 'Username exists'})
    else:
        return Response({'message': 'Username does not exist'})


@api_view(['POST'])
def create_user_and_profile(request):
    user_serializer = UserSerializer(data=request.data)
    
    if user_serializer.is_valid():
        user = user_serializer.save()
        user.set_password(user_serializer.validated_data['password'])  # Hash password before saving
        user.first_name = request.data.get('firstName', '')
        user.last_name = request.data.get('lastName', '')  
        user.save()
        
        profile_data = {
            'user': user.id,
            'address': request.data.get('address'),
            'phoneNb': request.data.get('phoneNb'),
        }
        profile_serializer = UserProfileSerializer(data=profile_data)
        
        if profile_serializer.is_valid():
            profile = profile_serializer.save()
            
            # Authenticate and login the user
            login_user = authenticate(username=user.username, password=request.data.get('password'))
            if login_user:
                login(request, login_user)  # This sets the user in the session
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'user': UserSerializer(user).data,
                    'userProfile': UserProfileSerializer(profile).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    "message": "You're successfully signed up and logged in."
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "User authentication failed after sign-up."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.delete()  # Optionally delete the user if profile creation fails
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'POST'])
# def user_list(request):

#     if request.method == 'GET':
#         users = UserProfile.objects.all()
#         serializer = UserProfileSerializer(users, many=True)
#         return JsonResponse({'users': serializer.data })
    
#     if request.method == 'POST':
#         serializer = UserProfileSerializer(data=request.data)
        
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
   # Fetch the UserProfile instance associated with the request user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Serialize the user profile
    serializer = UserProfileSerializer(user_profile)

    return Response(serializer.data)


#################### ITEMS ####################

@api_view(['GET'])
def filtered_items(request):
    section = request.query_params.get('section')
    category = request.query_params.get('category')
    size = request.query_params.get('size')
    priceRange = request.query_params.get('priceRange')
    color = request.query_params.get('color')
    item_type = request.query_params.get('item_type')  

    filters = Q()
    if section:
        filters &= Q(section=section)
    if category:
        filters &= Q(category=category)
    if size:
        filters &= Q(size=size)
    if item_type:
        filters &= Q(item_type=item_type)
    if color:
        filters &= Q(color=color)
    if priceRange:
        # Assuming priceRange is a string like '$10 - $20'
        min_price, max_price = map(str, priceRange.replace('\'', '').replace('$', '').split(' - '))
        filters &= Q(price__gte=min_price) & Q(price__lte=max_price)
    
    items = Item.objects.filter(filters).distinct()

    # Removing duplicates in Python
    unique_items = []
    unique_names = set()
    for item in items:
        if item.name not in unique_names:
            unique_names.add(item.name)
            unique_items.append(item)

    # Serialize and return the filtered items
    serializer = ItemSerializer(unique_items, many=True)
    return Response(serializer.data)

########################### ###########################################################
    
    

@api_view(['GET'])
def get_item(request, id):
    try:
        item = Item.objects.get(id=id)
    except Item.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ItemSerializer(item)
        return Response(serializer.data)
    


@api_view(['GET'])
def get_purchase_items(request, purchase_id):
    try:
        # Ensure the purchase exists
        purchase = get_object_or_404(Purchase, id=purchase_id)
        
        # Fetch all PurchaseItem instances related to the purchase
        purchase_items = PurchaseItem.objects.filter(purchase=purchase)
        
        # Extract the items from purchase_items
        items = [purchase_item.item for purchase_item in purchase_items]
        
        # Serialize the item details
        serializer = ItemSerializer(items, many=True)
        
        return Response(serializer.data)
    except Purchase.DoesNotExist:
        return Response({'message': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
def get_categories_by_section(request, section):
    # Filter items by the provided section and get unique categories
    categories = Item.objects.filter(section=section).values_list('category', flat=True).distinct()

    # Convert the QuerySet to a list to make it JSON serializable
    categories_list = list(categories)

    return Response(categories_list)


####################### PURCHASES ########################
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_purchases(request):
    user = request.user
    purchases = Purchase.objects.filter(customer=user)
    serializer = PurchaseSerializer(purchases, many=True)
    return Response(serializer.data)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_purchase(request):
    user = request.user
    data = request.data

    # Randomly generate delivery dates near the date of purchase
    today = timezone.now().date()
    delivery_date_start = today + timezone.timedelta(days=randint(1, 3))  # Start date 1-3 days from today
    delivery_date_end = delivery_date_start + timezone.timedelta(days=randint(1, 3))  # End date 1-3 days after start date

    # Create the purchase
    purchase = Purchase.objects.create(
        customer=user,
        total_price=data.get('totalPrice'),  # Assuming total_price is provided, or calculate from items
        delivery_date_start=delivery_date_start,
        delivery_date_end=delivery_date_end,
        status='Processing'  # Example status
    )

    # Create purchase items
    items = data.get('items')  # Assuming items is a list of item dictionaries with 'item_id' and 'quantity'
    for item_data in items:
        item = Item.objects.get(id=item_data.get('id'))
        purchased_quantity = item_data.get('quantity')

        PurchaseItem.objects.create(
            purchase=purchase,
            item=item,
            quantity=purchased_quantity
        )

         # Update the remaining quantity of the item
        item.remaining_quantity -= purchased_quantity
        item.save()  # Don't forget to save the item after updating

    serializer = PurchaseSerializer(purchase, context={'request': request})
    return Response(serializer.data)   


####################### FAVORITES ########################

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_favorites(request):
#     user = request.user
#     favorites = Favorite.objects.filter(user=user)
#     serializer = FavoriteSerializer(favorites, many=True)
#     return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_favorites(request):
    user = request.user
    # Fetch the favorited items directly
    favorited_items = Item.objects.filter(favorite__user=user)
    serializer = ItemSerializer(favorited_items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favorite(request):
    user = request.user
    item_id = request.data.get('item')
    item = get_object_or_404(Item, id=item_id)

    favorite, created = Favorite.objects.get_or_create(user=user, item=item)

    if created:
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({'detail': 'Item already in favorites'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_favorite(request, favorite_id):
    user = request.user
    try:
        favorite = Favorite.objects.get(id=favorite_id, user=user)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Favorite.DoesNotExist:
        return Response({'detail': 'Favorite not found.'}, status=status.HTTP_404_NOT_FOUND)


######################### To return item when adding to cart #################################
@api_view(['GET'])
def get_specific_item(request):
    section = request.query_params.get('section')
    category = request.query_params.get('category')
    name = request.query_params.get('name')
    size = request.query_params.get('size')
    color = request.query_params.get('color')

    #print("Received Params:", section, category, name, size, color)

    items = Item.objects.filter(
        section=section,
        category=category,
        name=name,
        size=size,
        color=color
    )

    #print("Filtered Items:", items)

    if items.exists():
        serializer = ItemSerializer(items.first())
        return Response(serializer.data)
    else:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
