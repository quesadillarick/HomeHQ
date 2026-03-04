from django.contrib import admin
from .models import Bill, Budget, BudgetExpense

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'frequency', 'due_date', 'is_paid']
    list_filter = ['frequency', 'is_paid']

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'limit', 'month', 'year']

admin.site.register(BudgetExpense)

from .models import CalendarEvent
@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'color']
