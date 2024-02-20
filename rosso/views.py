from .serializers import  ItemSerializer, PurchaseSerializer, PurchaseItemSerializer, FavoriteSerializer, UserSerializer
from .models import Item, Purchase, PurchaseItem, Favorite
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from random import randint
from rest_framework.response import Response
from rest_framework import status

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


@api_view(['GET'])
def filtered_items(request):
    # Capture 'section' and 'category' from the query parameters
    section = request.query_params.get('section')
    category = request.query_params.get('category')

    # Apply filters based on the presence of 'section' and 'category'
    filters = {}
    if section:
        filters['section'] = section
    if category:
        filters['category'] = category

    # Query the database for items matching the filters
    items = Item.objects.filter(**filters).distinct('name')

    # Serialize and return the filtered items
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)

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
def get_user_purchases(request, user_id):
    if request.method == 'GET':
        purchases = Purchase.objects.filter(customer_id = user_id)
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
        total_price=data.get('total_price'),  # Assuming total_price is provided, or calculate from items
        delivery_date_start=delivery_date_start,
        delivery_date_end=delivery_date_end,
        status='Processing'  # Example status
    )

    # Create purchase items
    items = data.get('items')  # Assuming items is a list of item dictionaries with 'item_id' and 'quantity'
    for item_data in items:
        item = Item.objects.get(id=item_data.get('item_id'))
        PurchaseItem.objects.create(
            purchase=purchase,
            item=item,
            quantity=item_data.get('quantity')
        )

    serializer = PurchaseSerializer(purchase, context={'request': request})
    return Response(serializer.data)   
    



