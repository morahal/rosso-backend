from .serializers import  ItemSerializer, PurchaseSerializer, PurchaseItemSerializer, FavoriteSerializer
from .models import Item, Purchase, PurchaseItem, Favorite
from rest_framework.decorators import api_view
from django.http import JsonResponse
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
def list_items(request):
    if request.method == 'GET':
        items = Item.objects.all()
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
    



