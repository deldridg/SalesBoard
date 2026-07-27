from django.db import models

# Create your models here.
class Salesperson(models.Model):
    REGION_CHOICES = [
        ('NSW', 'New South Wales'),
        ('VIC', 'Victoria'),
        ('QLD', 'Queensland'),
        ('WA', 'Western Australia'),
        ('SA', 'South Australia'),
        ('TAS', 'Tasmania'),
        ('ACT', 'Australian Capital Territory'),
        ('NT', 'Northern Territory'),       
    ]
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    email = models.EmailField(unique=True)
    region = models.CharField(max_length=3, choices=REGION_CHOICES)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Customer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    company = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company})"
    
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('services', 'Services'),
        ('consumables', 'Consumables'),
    ]
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    salesperson = models.ForeignKey(Salesperson, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.customer} - {self.product} ({self.date})"
    
    @property
    def total_value(self):
        return self.quantity * self.product.price
