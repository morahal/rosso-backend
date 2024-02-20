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
from .views import list_items, get_item, get_user_purchases

urlpatterns = [
    path('admin/', admin.site.urls),
    path('items/', list_items, name='list-items'),
    path('item/<int:id>/', get_item, name='get-item'),
    path('users/<int:user_id>/purchases/', get_user_purchases, name='user-purchases'),
]

