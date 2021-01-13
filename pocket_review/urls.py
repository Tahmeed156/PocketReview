from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('random/', views.random, name='random'),
    path('random/<str:tag_name>/', views.random, name='random')
]