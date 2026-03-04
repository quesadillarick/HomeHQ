from django.urls import path
from . import views

urlpatterns = [
    path('', views.asset_list, name='asset_list'),
    path('add/', views.asset_create, name='asset_create'),
    path('<int:pk>/edit/', views.asset_edit, name='asset_edit'),
    path('<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    path('loss-report/', views.loss_report, name='loss_report'),
    path('insurance/', views.insurance_list, name='insurance_list'),
    path('insurance/add/', views.insurance_create, name='insurance_create'),
    path('insurance/<int:pk>/edit/', views.insurance_edit, name='insurance_edit'),
    path('insurance/<int:pk>/delete/', views.insurance_delete, name='insurance_delete'),
]
