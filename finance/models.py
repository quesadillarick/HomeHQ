from django.db import models
from django.utils import timezone
import datetime
import calendar as cal_mod

FREQUENCY_CHOICES = [
    ('monthly', 'Monthly'),
    ('weekly', 'Weekly'),
    ('quarterly', 'Quarterly'),
    ('annually', 'Annually'),
    ('one_time', 'One Time'),
]

EVENT_FREQUENCY_CHOICES = [
    ('none',       'No Repeat'),
    ('weekly',     'Weekly'),
    ('biweekly',   'Bi-Weekly'),
    ('monthly',    'Monthly'),
    ('quarterly',  'Quarterly'),
    ('annually',   'Annually'),
]

EVENT_COLOR_CHOICES = [
    ('blue',   'Blue'),
    ('green',  'Green'),
    ('yellow', 'Yellow'),
    ('red',    'Red'),
    ('purple', 'Purple'),
]


# ── Bill ──────────────────────────────────────────────────────────────────────

class Bill(models.Model):
    name      = models.CharField(max_length=200)
    amount    = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    due_date  = models.DateField()
    url       = models.URLField(max_length=500, blank=True, help_text="Optional link to the bill's payment page")
    notes     = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, help_text="Uncheck to stop tracking in future months")
    created_at = models.DateTimeField(auto_now_add=True)

    # legacy — kept for data safety
    is_paid       = models.BooleanField(default=False)
    last_paid_date = models.DateField(null=True, blank=True)

    def applies_to_month(self, month, year):
        d = self.due_date
        if self.frequency == 'one_time':
            return d.month == month and d.year == year
        elif self.frequency == 'monthly':
            return (year, month) >= (d.year, d.month)
        elif self.frequency == 'annually':
            return d.month == month and year >= d.year
        elif self.frequency == 'quarterly':
            months_diff = (year - d.year) * 12 + (month - d.month)
            return months_diff >= 0 and months_diff % 3 == 0
        elif self.frequency == 'weekly':
            return (year, month) >= (d.year, d.month)
        return False

    def due_date_for_month(self, month, year):
        day = self.due_date.day
        last_day = cal_mod.monthrange(year, month)[1]
        return datetime.date(year, month, min(day, last_day))

    def payment_for_month(self, month, year):
        try:
            return self.payments.get(month=month, year=year)
        except BillPayment.DoesNotExist:
            return None

    def __str__(self):
        return f"{self.name} — ${self.amount}"

    class Meta:
        ordering = ['due_date']


class BillPayment(models.Model):
    bill      = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    month     = models.IntegerField()
    year      = models.IntegerField()
    paid_date = models.DateField(null=True, blank=True)
    notes     = models.TextField(blank=True)

    class Meta:
        unique_together = ['bill', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.bill.name} — {self.month}/{self.year} (Paid)"


# ── Budget ─────────────────────────────────────────────────────────────────────

class Budget(models.Model):
    category = models.CharField(max_length=100)
    limit    = models.DecimalField(max_digits=10, decimal_places=2)
    month    = models.IntegerField()
    year     = models.IntegerField()

    @property
    def spent(self):
        return sum(e.amount for e in self.expenses.all())

    @property
    def remaining(self):
        return self.limit - self.spent

    @property
    def percentage(self):
        if self.limit > 0:
            return min(int(self.spent / self.limit * 100), 100)
        return 0

    def __str__(self):
        return f"{self.category} ({self.month}/{self.year})"

    class Meta:
        unique_together = ['category', 'month', 'year']


class BudgetExpense(models.Model):
    budget      = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=200)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    date        = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.description} — ${self.amount}"

    class Meta:
        ordering = ['-date']


# ── Calendar Event ─────────────────────────────────────────────────────────────

class CalendarEvent(models.Model):
    title     = models.CharField(max_length=200)
    date      = models.DateField()
    end_date  = models.DateField(null=True, blank=True, help_text="For multi-day single events; ignored when repeating")
    frequency = models.CharField(max_length=20, choices=EVENT_FREQUENCY_CHOICES, default='none',
                                  help_text="How often this event repeats")
    repeat_until = models.DateField(null=True, blank=True,
                                     help_text="Last date to generate occurrences (leave blank for indefinite)")
    color     = models.CharField(max_length=20, choices=EVENT_COLOR_CHOICES, default='blue')
    notes     = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_recurring(self):
        return self.frequency != 'none'

    def occurrences_in_month(self, month, year):
        """
        Return a list of (start_date, end_date | None) tuples for every
        occurrence of this event that falls within the given month/year.
        """
        import calendar as _cal
        last_day   = _cal.monthrange(year, month)[1]
        month_start = datetime.date(year, month, 1)
        month_end   = datetime.date(year, month, last_day)
        cutoff      = self.repeat_until or datetime.date(year + 5, 1, 1)

        if self.frequency == 'none':
            # Single event — include if it overlaps the month
            end = self.end_date or self.date
            if self.date <= month_end and end >= month_start:
                return [(self.date, self.end_date)]
            return []

        results = []
        cursor  = self.date

        # Fast-forward: skip to first occurrence on/after month_start
        if self.frequency == 'weekly':
            delta_days = (month_start - cursor).days
            if delta_days > 0:
                weeks_ahead = delta_days // 7
                cursor += datetime.timedelta(weeks=weeks_ahead)
        elif self.frequency == 'biweekly':
            delta_days = (month_start - cursor).days
            if delta_days > 0:
                fortnights = delta_days // 14
                cursor += datetime.timedelta(weeks=fortnights * 2)
        elif self.frequency in ('monthly', 'quarterly', 'annually'):
            # Jump straight to the correct month
            if cursor < month_start:
                if self.frequency == 'monthly':
                    cursor = cursor.replace(year=year, month=month)
                elif self.frequency == 'quarterly':
                    months_diff = (year - self.date.year) * 12 + (month - self.date.month)
                    q = months_diff // 3
                    target_month = self.date.month + q * 3
                    target_year  = self.date.year + (target_month - 1) // 12
                    target_month = ((target_month - 1) % 12) + 1
                    try:
                        cursor = cursor.replace(year=target_year, month=target_month)
                    except ValueError:
                        cursor = cursor.replace(year=target_year, month=target_month,
                                                 day=min(cursor.day, _cal.monthrange(target_year, target_month)[1]))
                elif self.frequency == 'annually':
                    if (self.date.month, self.date.day) != (month, self.date.day):
                        return []   # annual event isn't in this month
                    try:
                        cursor = cursor.replace(year=year)
                    except ValueError:
                        cursor = cursor.replace(year=year, day=28)

        # Walk forward collecting matches within the month
        max_iters = 60   # safety cap
        iters = 0
        while cursor <= month_end and cursor <= cutoff and iters < max_iters:
            iters += 1
            if cursor >= month_start:
                results.append((cursor, None))

            # Advance
            if self.frequency == 'weekly':
                cursor += datetime.timedelta(weeks=1)
            elif self.frequency == 'biweekly':
                cursor += datetime.timedelta(weeks=2)
            elif self.frequency == 'monthly':
                m = cursor.month + 1 if cursor.month < 12 else 1
                y = cursor.year if cursor.month < 12 else cursor.year + 1
                d = min(cursor.day, _cal.monthrange(y, m)[1])
                cursor = cursor.replace(year=y, month=m, day=d)
            elif self.frequency == 'quarterly':
                m = cursor.month + 3
                y = cursor.year + (m - 1) // 12
                m = ((m - 1) % 12) + 1
                d = min(cursor.day, _cal.monthrange(y, m)[1])
                cursor = cursor.replace(year=y, month=m, day=d)
            elif self.frequency == 'annually':
                try:
                    cursor = cursor.replace(year=cursor.year + 1)
                except ValueError:
                    cursor = cursor.replace(year=cursor.year + 1, day=28)
            else:
                break   # 'none' should not reach here

        return results

    def __str__(self):
        return f"{self.title} ({self.date})"

    class Meta:
        ordering = ['date']
