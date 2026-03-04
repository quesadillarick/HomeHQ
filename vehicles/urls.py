from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehicle_list, name='vehicle_list'),
    path('add/', views.vehicle_create, name='vehicle_create'),
    path('<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('<int:pk>/service/add/', views.service_add, name='service_add'),
    path('service/<int:pk>/delete/', views.service_delete, name='service_delete'),
]
