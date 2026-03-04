from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from finance.models import Bill, Budget, BudgetExpense, CalendarEvent
from assets.models import Asset
from vehicles.models import Vehicle, ServiceLog
from notes.models import Note
import datetime
import json

@login_required
def dashboard(request):
    today = timezone.now().date()
    upcoming_bills = Bill.objects.filter(is_paid=False, due_date__lte=today + datetime.timedelta(days=14)).order_by('due_date')
    overdue_bills = Bill.objects.filter(is_paid=False, due_date__lt=today)
    total_assets = sum(a.value for a in Asset.objects.all())
    vehicles = Vehicle.objects.all()
    service_alerts = []
    for v in vehicles:
        last_log = ServiceLog.objects.filter(vehicle=v).order_by('-date').first()
        if last_log and v.odometer and last_log.next_service_odometer:
            if v.odometer >= last_log.next_service_odometer:
                service_alerts.append(v)
    recent_notes = Note.objects.order_by('-created_at')[:5]

    # Budget summary for current month
    now = timezone.now()
    budgets = Budget.objects.filter(month=now.month, year=now.year)
    budget_data = []
    for b in budgets:
        spent = sum(e.amount for e in b.expenses.all())
        pct = int((spent / b.limit * 100)) if b.limit > 0 else 0
        budget_data.append({'budget': b, 'spent': spent, 'pct': min(pct, 100)})

    # Upcoming calendar events (next 30 days)
    upcoming_events = CalendarEvent.objects.filter(
        date__gte=today,
        date__lte=today + datetime.timedelta(days=30)
    ).order_by('date')[:5]

    context = {
        'upcoming_bills': upcoming_bills,
        'overdue_bills': overdue_bills,
        'overdue_count': overdue_bills.count(),
        'total_assets': total_assets,
        'vehicle_count': vehicles.count(),
        'service_alerts': service_alerts,
        'recent_notes': recent_notes,
        'budget_data': budget_data[:4],
        'upcoming_events': upcoming_events,
        'today': today,
        'today_iso': today.isoformat(),
        'dow_labels': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    }
    return render(request, 'dashboard.html', context)
