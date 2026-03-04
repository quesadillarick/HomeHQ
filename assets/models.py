from django.db import models

ASSET_CATEGORY_CHOICES = [
    ('electronics', 'Electronics'),
    ('jewelry', 'Jewelry'),
    ('tools', 'Tools'),
    ('furniture', 'Furniture'),
    ('appliances', 'Appliances'),
    ('collectibles', 'Collectibles'),
    ('other', 'Other'),
]

class InsurancePolicy(models.Model):
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=100)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.provider})"

class Asset(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=ASSET_CATEGORY_CHOICES, default='other')
    value = models.DecimalField(max_digits=12, decimal_places=2)
    serial_number = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    insurance_policy = models.ForeignKey(InsurancePolicy, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    manual = models.FileField(upload_to='manuals/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['category', 'name']
