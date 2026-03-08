from django.urls import path
from . import views

urlpatterns = [
    path('', views.finance_home, name='finance_home'),
    # Bills
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/add/', views.bill_create, name='bill_create'),
    path('bills/export/', views.bill_export, name='bill_export'),
    path('bills/import/', views.bill_import, name='bill_import'),
    path('bills/report/', views.bill_report, name='bill_report'),
    path('bills/<int:pk>/edit/', views.bill_edit, name='bill_edit'),
    path('bills/<int:pk>/delete/', views.bill_delete, name='bill_delete'),
    path('bills/<int:pk>/mark-paid/', views.mark_paid, name='bill_mark_paid'),
    path('bills/<int:pk>/mark-unpaid/', views.mark_unpaid, name='bill_mark_unpaid'),
    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.budget_create, name='budget_create'),
    path('budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),
    path('budgets/<int:pk>/expense/add/', views.expense_add, name='expense_add'),
    path('budgets/expense/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    # Calendar events
    path('events/add/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('calendar/data/', views.calendar_data, name='calendar_data'),
]
