import datetime
import calendar as cal_mod
import json
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Bill, BillPayment, Budget, BudgetExpense, CalendarEvent
from .forms import BillForm, BudgetForm, BudgetExpenseForm, CalendarEventForm


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_month_year(request):
    today = timezone.now().date()
    try:
        month = int(request.GET.get('month', today.month))
        year  = int(request.GET.get('year',  today.year))
        month = max(1, min(12, month))
        year  = max(2000, min(2100, year))
    except (TypeError, ValueError):
        month, year = today.month, today.year
    return month, year


def _prev_month(month, year):
    return (12, year - 1) if month == 1 else (month - 1, year)


def _next_month(month, year):
    return (1, year + 1) if month == 12 else (month + 1, year)


def _bills_for_month(month, year):
    today = timezone.now().date()
    active = Bill.objects.filter(is_active=True)
    inactive_paid = Bill.objects.filter(
        is_active=False, payments__month=month, payments__year=year
    )
    all_bills = (active | inactive_paid).distinct()
    result = []
    for bill in all_bills:
        if not bill.applies_to_month(month, year):
            continue
        due     = bill.due_date_for_month(month, year)
        payment = bill.payment_for_month(month, year)
        is_paid = payment is not None
        result.append({
            'bill':      bill,
            'due':       due,
            'is_paid':   is_paid,
            'is_overdue': not is_paid and due < today,
            'paid_date': payment.paid_date if payment else None,
            'payment':   payment,
        })
    result.sort(key=lambda x: x['due'])
    return result


# ── Bill views ─────────────────────────────────────────────────────────────────

@login_required
def finance_home(request):
    return redirect('bill_list')


@login_required
def bill_list(request):
    month, year = _parse_month_year(request)
    today = timezone.now().date()
    bill_rows = _bills_for_month(month, year)
    total_due    = sum(r['bill'].amount for r in bill_rows)
    total_paid   = sum(r['bill'].amount for r in bill_rows if r['is_paid'])
    total_unpaid = total_due - total_paid
    return render(request, 'finance/bill_list.html', {
        'bill_rows':      bill_rows,
        'month':          month,
        'year':           year,
        'month_name':     datetime.date(year, month, 1).strftime('%B %Y'),
        'prev_month':     _prev_month(month, year)[0],
        'prev_year':      _prev_month(month, year)[1],
        'next_month':     _next_month(month, year)[0],
        'next_year':      _next_month(month, year)[1],
        'total_due':      total_due,
        'total_paid':     total_paid,
        'total_unpaid':   total_unpaid,
        'paid_count':     sum(1 for r in bill_rows if r['is_paid']),
        'overdue_count':  sum(1 for r in bill_rows if r['is_overdue']),
        'bill_count':     len(bill_rows),
        'today':          today,
        'is_current_month': month == today.month and year == today.year,
    })


@login_required
def bill_create(request):
    form = BillForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Bill added.')
        return redirect('bill_list')
    return render(request, 'finance/bill_form.html', {'form': form, 'title': 'Add Bill'})


@login_required
def bill_edit(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    form = BillForm(request.POST or None, instance=bill)
    if form.is_valid():
        form.save()
        messages.success(request, 'Bill updated.')
        return redirect('bill_list')
    return render(request, 'finance/bill_form.html', {'form': form, 'title': 'Edit Bill'})


@login_required
def bill_delete(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        bill.delete()
        messages.success(request, 'Bill deleted.')
        return redirect('bill_list')
    return render(request, 'confirm_delete.html', {'obj': bill, 'cancel_url': 'bill_list'})


@login_required
def mark_paid(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        month = int(request.POST.get('month', timezone.now().month))
        year  = int(request.POST.get('year',  timezone.now().year))
        BillPayment.objects.get_or_create(
            bill=bill, month=month, year=year,
            defaults={'paid_date': timezone.now().date()}
        )
        messages.success(request, f'"{bill.name}" marked paid for {datetime.date(year, month, 1).strftime("%B %Y")}.')
    return redirect(f'/finance/bills/?month={request.POST.get("month","")}&year={request.POST.get("year","")}')


@login_required
def mark_unpaid(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        month = int(request.POST.get('month', timezone.now().month))
        year  = int(request.POST.get('year',  timezone.now().year))
        BillPayment.objects.filter(bill=bill, month=month, year=year).delete()
        messages.success(request, f'"{bill.name}" marked unpaid for {datetime.date(year, month, 1).strftime("%B %Y")}.')
    return redirect(f'/finance/bills/?month={request.POST.get("month","")}&year={request.POST.get("year","")}')


# ── Bill Export / Import ───────────────────────────────────────────────────────

@login_required
def bill_export(request):
    """Export all bills (definitions only) to a JSON file download."""
    bills = Bill.objects.all().order_by('pk')
    data = {
        'homehq_export': 'bills',
        'version': 1,
        'exported_at': timezone.now().isoformat(),
        'bills': [
            {
                'name':      b.name,
                'amount':    str(b.amount),
                'frequency': b.frequency,
                'due_date':  b.due_date.isoformat(),
                'url':       b.url,
                'notes':     b.notes,
                'is_active': b.is_active,
            }
            for b in bills
        ],
    }
    payload = json.dumps(data, indent=2)
    response = HttpResponse(payload, content_type='application/json')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="homehq_bills_{timestamp}.json"'
    return response


@login_required
def bill_import(request):
    """Import bills from a JSON file upload."""
    if request.method == 'GET':
        return render(request, 'finance/bill_import.html')

    uploaded = request.FILES.get('import_file')
    if not uploaded:
        messages.error(request, 'No file selected.')
        return redirect('bill_import')

    try:
        raw  = uploaded.read().decode('utf-8')
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        messages.error(request, f'Invalid JSON file: {e}')
        return redirect('bill_import')

    if data.get('homehq_export') != 'bills':
        messages.error(request, 'This file does not appear to be a HomeHQ bills export.')
        return redirect('bill_import')

    mode    = request.POST.get('import_mode', 'skip')   # skip | overwrite | append
    created = 0
    skipped = 0
    updated = 0
    errors  = []

    for i, item in enumerate(data.get('bills', []), start=1):
        try:
            name = item['name'].strip()
            if not name:
                errors.append(f'Row {i}: empty name, skipped.')
                continue

            existing = Bill.objects.filter(name__iexact=name).first()

            fields = {
                'amount':    Decimal(item['amount']),
                'frequency': item.get('frequency', 'monthly'),
                'due_date':  datetime.date.fromisoformat(item['due_date']),
                'url':       item.get('url', ''),
                'notes':     item.get('notes', ''),
                'is_active': item.get('is_active', True),
            }

            if existing:
                if mode == 'overwrite':
                    for k, v in fields.items():
                        setattr(existing, k, v)
                    existing.save()
                    updated += 1
                else:
                    skipped += 1
            else:
                Bill.objects.create(name=name, **fields)
                created += 1

        except Exception as e:
            errors.append(f'Row {i} ({item.get("name","?")}): {e}')

    parts = []
    if created: parts.append(f'{created} created')
    if updated: parts.append(f'{updated} updated')
    if skipped: parts.append(f'{skipped} skipped (already exist)')
    summary = ', '.join(parts) if parts else 'No changes made'
    messages.success(request, f'Import complete — {summary}.')
    for err in errors:
        messages.warning(request, err)
    return redirect('bill_list')


# ── Budget views ───────────────────────────────────────────────────────────────

@login_required
def budget_list(request):
    now   = timezone.now()
    month = int(request.GET.get('month', now.month))
    year  = int(request.GET.get('year',  now.year))
    budgets = Budget.objects.filter(month=month, year=year)
    budget_data = [{'budget': b, 'spent': b.spent, 'remaining': b.remaining, 'pct': b.percentage} for b in budgets]
    return render(request, 'finance/budget_list.html', {
        'budget_data': budget_data, 'month': month, 'year': year,
        'month_name': datetime.datetime(year, month, 1).strftime('%B %Y'),
    })


@login_required
def budget_create(request):
    form = BudgetForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Budget created.')
        return redirect('budget_list')
    return render(request, 'finance/budget_form.html', {'form': form, 'title': 'Create Budget'})


@login_required
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    form   = BudgetForm(request.POST or None, instance=budget)
    if form.is_valid():
        form.save()
        messages.success(request, 'Budget updated.')
        return redirect('budget_list')
    return render(request, 'finance/budget_form.html', {'form': form, 'title': 'Edit Budget'})


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted.')
        return redirect('budget_list')
    return render(request, 'confirm_delete.html', {'obj': budget, 'cancel_url': 'budget_list'})


@login_required
def expense_add(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    form   = BudgetExpenseForm(request.POST or None)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.budget = budget
        expense.save()
        messages.success(request, 'Expense logged.')
        return redirect('budget_list')
    return render(request, 'finance/expense_form.html', {'form': form, 'budget': budget})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(BudgetExpense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense removed.')
    return redirect('budget_list')


# ── Calendar Event views ───────────────────────────────────────────────────────

@login_required
def event_create(request):
    initial = {'date': request.GET.get('date', '')}
    form = CalendarEventForm(request.POST or None, initial=initial)
    if form.is_valid():
        form.save()
        messages.success(request, 'Event added.')
        return redirect('dashboard')
    return render(request, 'finance/event_form.html', {'form': form, 'title': 'Add Event'})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk)
    form  = CalendarEventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, 'Event updated.')
        return redirect('dashboard')
    return render(request, 'finance/event_form.html', {'form': form, 'title': 'Edit Event'})


@login_required
def event_delete(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted.')
    return redirect('dashboard')


@login_required
def calendar_data(request):
    """JSON: bills + calendar events (with recurrence expansion) for month/year."""
    try:
        month = int(request.GET.get('month'))
        year  = int(request.GET.get('year'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid params'}, status=400)

    today = timezone.now().date()
    items = []

    # Bills
    for row in _bills_for_month(month, year):
        bill = row['bill']
        items.append({
            'id':         f'bill-{bill.pk}-{month}-{year}',
            'type':       'bill',
            'title':      bill.name,
            'date':       row['due'].isoformat(),
            'amount':     float(bill.amount),
            'is_paid':    row['is_paid'],
            'is_overdue': row['is_overdue'],
            'url':        bill.url,
            'edit_url':   f'/finance/bills/{bill.pk}/edit/',
        })

    # Calendar events — expand recurrences
    all_events = CalendarEvent.objects.all()
    for event in all_events:
        for (occ_start, occ_end) in event.occurrences_in_month(month, year):
            items.append({
                'id':         f'event-{event.pk}-{occ_start.isoformat()}',
                'type':       'event',
                'title':      event.title,
                'date':       occ_start.isoformat(),
                'end_date':   occ_end.isoformat() if occ_end else None,
                'color':      event.color,
                'frequency':  event.frequency,
                'notes':      event.notes,
                'is_recurring': event.is_recurring(),
                'edit_url':   f'/finance/events/{event.pk}/edit/',
                'delete_url': f'/finance/events/{event.pk}/delete/',
            })

    return JsonResponse({'items': items})
