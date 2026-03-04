from django.db import models
from django.utils import timezone

SERVICE_TYPE_CHOICES = [
    ('oil_change', 'Oil Change'),
    ('tires', 'Tires'),
    ('brakes', 'Brakes'),
    ('inspection', 'Inspection'),
    ('repair', 'Repair'),
    ('other', 'Other'),
]

class Vehicle(models.Model):
    vin = models.CharField(max_length=17, blank=True)
    year = models.IntegerField()
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    color = models.CharField(max_length=50, blank=True)
    plate = models.CharField(max_length=20, blank=True)
    odometer = models.IntegerField(null=True, blank=True, help_text="Current odometer in miles")
    insurance_policy = models.CharField(max_length=200, blank=True)
    title_scan = models.FileField(upload_to='vehicle_docs/', null=True, blank=True)
    registration_scan = models.FileField(upload_to='vehicle_docs/', null=True, blank=True)
    notes = models.TextField(blank=True)

    @property
    def service_due(self):
        last_oil = ServiceLog.objects.filter(vehicle=self, service_type='oil_change').order_by('-date').first()
        if last_oil and last_oil.next_service_odometer and self.odometer:
            return self.odometer >= last_oil.next_service_odometer
        return False

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"


class ServiceLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='service_logs')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    date = models.DateField(default=timezone.now)
    odometer_at_service = models.IntegerField(null=True, blank=True)
    next_service_odometer = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shop = models.CharField(max_length=200, blank=True)
    receipt_scan = models.FileField(upload_to='service_receipts/', null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.get_service_type_display()} on {self.date}"

    class Meta:
        ordering = ['-date']
