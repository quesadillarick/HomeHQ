from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from finance.models import Bill, Budget, CalendarEvent
from finance.views import _bills_for_month
from assets.models import Asset
from vehicles.models import Vehicle, ServiceLog
from notes.models import Note
import datetime


@login_required
def dashboard(request):
    today = timezone.now().date()
    now   = timezone.now()

    # ── Bills: use per-month payment logic, not legacy Bill.is_paid ──────────
    current_bill_rows = _bills_for_month(today.month, today.year)

    overdue_rows  = [r for r in current_bill_rows if r['is_overdue']]
    upcoming_rows = [
        r for r in current_bill_rows
        if not r['is_paid']
        and not r['is_overdue']
        and r['due'] <= today + datetime.timedelta(days=14)
    ]

    # ── Assets / Vehicles ─────────────────────────────────────────────────────
    total_assets = sum(a.value for a in Asset.objects.all())
    vehicles     = Vehicle.objects.all()
    service_alerts = []
    for v in vehicles:
        last_log = ServiceLog.objects.filter(vehicle=v).order_by('-date').first()
        if last_log and v.odometer and last_log.next_service_odometer:
            if v.odometer >= last_log.next_service_odometer:
                service_alerts.append(v)

    # ── Notes ─────────────────────────────────────────────────────────────────
    recent_notes = Note.objects.order_by('-created_at')[:5]

    # ── Budget summary for current month ─────────────────────────────────────
    budgets = Budget.objects.filter(month=now.month, year=now.year)
    budget_data = []
    for b in budgets:
        spent = sum(e.amount for e in b.expenses.all())
        pct   = int((spent / b.limit * 100)) if b.limit > 0 else 0
        budget_data.append({'budget': b, 'spent': spent, 'pct': min(pct, 100)})

    # ── Upcoming calendar events (next 30 days) ───────────────────────────────
    upcoming_events = CalendarEvent.objects.filter(
        date__gte=today,
        date__lte=today + datetime.timedelta(days=30)
    ).order_by('date')[:5]

    context = {
        # Bill rows (dicts with bill, due, is_paid, is_overdue, paid_amount…)
        'upcoming_rows':  upcoming_rows,
        'overdue_rows':   overdue_rows,
        'overdue_count':  len(overdue_rows),
        # Assets / vehicles
        'total_assets':   total_assets,
        'vehicle_count':  vehicles.count(),
        'service_alerts': service_alerts,
        # Notes / budget / events
        'recent_notes':   recent_notes,
        'budget_data':    budget_data[:4],
        'upcoming_events':upcoming_events,
        # Calendar helpers
        'today':          today,
        'today_iso':      today.isoformat(),
        'dow_labels':     ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    }
    return render(request, 'dashboard.html', context)
