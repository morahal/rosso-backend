from decimal import Decimal
from .serializers import  ItemSerializer, PurchaseSerializer, PurchaseItemSerializer, FavoriteSerializer, UserSerializer
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
    # The request.user property will contain the user instance associated with the provided token
    user = request.user
    serializer = UserSerializer(user)
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
    # Access the authenticated user from the request
    user = request.user
    
    # Filter purchases by the authenticated user's ID
    purchases = Purchase.objects.filter(customer=user)
    
    # Serialize the purchase data
    serializer = PurchaseSerializer(purchases, many=True)
    
    # Return the serialized data in the response
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
        total_price=data.get('total_price'),  # Assuming total_price is provided, or calculate from items
        delivery_date_start=delivery_date_start,
        delivery_date_end=delivery_date_end,
        status='Processing'  # Example status
    )

    # Create purchase items
    items = data.get('items')  # Assuming items is a list of item dictionaries with 'item_id' and 'quantity'
    for item_data in items:
        item = Item.objects.get(id=item_data.get('id'))
        PurchaseItem.objects.create(
            purchase=purchase,
            item=item,
            quantity=item_data.get('quantity')
        )

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


########## To return item when adding to cart ########
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
