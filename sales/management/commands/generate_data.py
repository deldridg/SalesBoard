import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from sales.models import Salesperson, Customer, Product, Sale
import datetime

fake = Faker("en_AU")

def gendered_name(gender):
    """Return a full name consistent with the given gender ('M' or 'F')."""
    if gender == 'M':
        return f"{fake.first_name_male()} {fake.last_name}"
    return f"{fake.first_name_female()} {fake.last_name}"

class Command(BaseCommand):
    help = 'Generate realistic fake sales data'
    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        Sale.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        Salesperson.objects.all().delete()
        # --- Salespeople ---
        regions = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']
        salespeople = []
        for _ in range(8):
            gender = random.choice(['M', 'F'])
            sp = Salesperson.objects.create(
                name=gendered_name(gender),
                gender=gender,
                email=fake.unique.email(),
                region=random.choice(regions),
                phone=fake.phone_number()[:20],
            )
            salespeople.append(sp)
        self.stdout.write(f'  Created {len(salespeople)} salespeople')
        # --- Products ---
        product_data = [
            ('Laptop Pro 15"', 'hardware', Decimal('2499.00'), 'HW-001'),
            ('Wireless Mouse', 'hardware', Decimal('79.00'), 'HW-002'),
            ('USB-C Hub 7-port', 'hardware', Decimal('129.00'), 'HW-003'),
            ('Standing Desk', 'hardware', Decimal('899.00'), 'HW-004'),
            ('4K Monitor 27"', 'hardware', Decimal('749.00'), 'HW-005'),
            ('CRM Suite (annual)', 'software', Decimal('1200.00'), 'SW-001'),
            ('Accounting Pro', 'software', Decimal('599.00'), 'SW-002'),
            ('Security Suite', 'software', Decimal('449.00'), 'SW-003'),
            ('Cloud Backup 1TB', 'software', Decimal('199.00'), 'SW-004'),
            ('Project Manager Pro', 'software', Decimal('349.00'), 'SW-005'),
            ('On-site Setup', 'services', Decimal('350.00'), 'SV-001'),
            ('Training Day (5 users)', 'services', Decimal('800.00'), 'SV-002'),
            ('Annual Support Plan', 'services', Decimal('1500.00'), 'SV-003'),
            ('Printer Paper (box)', 'consumables', Decimal('45.00'), 'CN-001'),
            ('Ink Cartridge Set', 'consumables', Decimal('89.00'), 'CN-002'),
        ]
        products = []
        for name, cat, price, sku in product_data:
            p = Product.objects.create(
                name=name, category=cat, price=price, sku=sku,
                description=fake.sentence()
            )
            products.append(p)
        self.stdout.write(f'  Created {len(products)} products')
        # --- Customers ---
        states = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']
        customers = []
        for _ in range(40):
            gender = random.choice(['M', 'F'])
            c = Customer.objects.create(
                name=gendered_name(gender),
                gender=gender,
                company=fake.company(),
                email=fake.unique.email(),
                phone=fake.phone_number()[:20],
                address=fake.street_address(),
                city=fake.city(),
                state=random.choice(states),
                postcode=fake.postcode(),
            )
            customers.append(c)
        self.stdout.write(f'  Created {len(customers)} customers')
        # --- Sales ---
        statuses = ['pending', 'won', 'won', 'won', 'lost', 'cancelled']
        today = datetime.date.today()
        count = 0
        for _ in range(250):
            days_ago = random.randint(1, 730)
            sale_date = today - datetime.timedelta(days=days_ago)
            Sale.objects.create(
                customer=random.choice(customers),
                salesperson=random.choice(salespeople),
                product=random.choice(products),
                quantity=random.randint(1, 10),
                date=sale_date,
                status=random.choice(statuses),
                notes=fake.sentence() if random.random() > 0.6 else '',
            )
            count += 1
        self.stdout.write(f'  Created {count} sales records')
        self.stdout.write(self.style.SUCCESS('Done! Database seeded.'))