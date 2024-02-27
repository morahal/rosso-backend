"""
URL configuration for rosso project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from rosso import settings
from .views import filtered_items, get_item, get_specific_item, get_user_purchases, get_user, create_purchase, list_favorites, add_favorite, remove_favorite, get_categories_by_section, create_user_and_profile, check_username_exists, login_view
from django.contrib.auth.views import LogoutView, LoginView
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# class CustomLoginView(LoginView):
#     pass

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/info/', get_user, name='get-user'),
    path('items/', filtered_items, name='list-items'),
    path('item/<int:id>/', get_item, name='get-item'),
    path('categories/<section>/', get_categories_by_section, name='categories-by-section'),
    path('users/<int:user_id>/purchases/', get_user_purchases, name='user-purchases'),
    path('purchase/create/', create_purchase, name='create-purchase'),
    path('favorites/', list_favorites, name='list-favorites'),
    path('favorites/add/', add_favorite, name='add-favorite'),
    path('favorites/remove/<int:favorite_id>/', remove_favorite, name='remove-favorite'),
    path('specificItem/', get_specific_item, name='get-specific-item'),
    path('createUser/', create_user_and_profile, name='create-user'),
    path('checkUsername/<str:username>/', check_username_exists, name='check-username'),
     path('login/', login_view, name='login'),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)