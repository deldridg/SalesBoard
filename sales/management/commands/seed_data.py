from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import timedelta, date
from sales.models import Salesperson, Customer, Product, Sale

fake = Faker('en_AU')

class Command(BaseCommand):
    help = 'Generate realistic sample data for SalesBoard (Hiking/Outdoor Shop)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting data generation...'))

        # Clear existing data (optional - comment out if you want to append)
        Salesperson.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()
        Sale.objects.all().delete()

        # ==================== SALESPERSONS ====================
        
        self.stdout.write('Creating Salespeople...')
        REGION_CHOICES = [code for code, _ in Salesperson.REGION_CHOICES]
        
        for region in REGION_CHOICES:
            for _ in range(random.randint(2, 3)):
                gender = random.choice(['M', 'F'])
                first_name = fake.first_name_male() if gender == 'M' else fake.first_name_female()
                
                Salesperson.objects.create(
                    first_name=first_name,
                    last_name=fake.last_name(),
                    gender=gender,
                    email=fake.unique.email(),
                    region=region,
                    phone=fake.phone_number()[:20],
                )

        salespeople = list(Salesperson.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(salespeople)} salespeople'))

        # ==================== PRODUCTS ====================
        self.stdout.write('Creating Products...')

        product_data = {
            'hardware': [
                ("Osprey Atmos 65L Backpack", 349.99),
                ("Black Diamond Hiking Poles", 129.99),
                ("MSR PocketRocket Stove", 89.95),
                ("Sea to Summit Sleeping Mat", 149.99),
                ("Petzl Headlamp", 89.95),
            ],
            'software': [
                ("AllTrails Premium Annual", 49.99),
                ("Garmin inReach Mini 2", 399.99),
                ("Strava Summit", 79.99),
            ],
            'services': [
                ("Guided Blue Mountains Day Hike", 249.00),
                ("Wilderness First Aid Course", 189.00),
                ("Custom Pack Fitting", 89.00),
            ],
            'consumables': [
                ("Dehydrated Hiking Meals (10 pack)", 89.99),
                ("Water Purification Tablets", 19.99),
                ("Trail Mix Bulk Pack", 24.99),
                ("Sunscreen SPF50+", 14.99),
            ]
        }

        sku_counter = 1000
        for category, items in product_data.items():
            for name, price in items:
                Product.objects.create(
                    name=name,
                    category=category,
                    price=price,
                    description=fake.sentence(nb_words=6),
                    sku=f"HB{sku_counter}"
                )
                sku_counter += 1

        # Extra random products
        for _ in range(30):
            Product.objects.create(
                name=fake.catch_phrase().title(),
                category=random.choice(list(product_data.keys())),
                price=round(random.uniform(15, 650), 2),
                description=fake.sentence(nb_words=8),
                sku=f"HB{sku_counter}"
            )
            sku_counter += 1

        products = list(Product.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))

        # ==================== CUSTOMERS ====================
        self.stdout.write('Creating Customers...')
        states = {code: name for code, name in Salesperson.REGION_CHOICES}

        for region in REGION_CHOICES:
            for _ in range(random.randint(20, 30)):
                gender = random.choice(['M', 'F'])
                first_name = fake.first_name_male() if gender == 'M' else fake.first_name_female()

                Customer.objects.create(
                    first_name=first_name,
                    last_name=fake.last_name(),
                    gender=gender,
                    company=fake.company(),
                    email=fake.unique.email(),
                    phone=fake.phone_number()[:20],
                    address=fake.street_address(),
                    city=fake.city(),
                    state=states.get(region, 'New South Wales'),
                    postcode=fake.postcode(),
                )

        customers = list(Customer.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(customers)} customers'))

        # ==================== SALES ====================
        self.stdout.write('Creating Sales (100-200 per region)...')
        
        STATUS_CHOICES = ['pending', 'won', 'lost', 'cancelled']
        start_date = date(2024, 1, 1)
        
        sales_created = 0

        for region in REGION_CHOICES:
            # Get regional salespeople and customers
            regional_salespeople = [sp for sp in salespeople if sp.region == region]
            regional_customers = [c for c in customers if c.state == states.get(region)]

            if not regional_salespeople or not regional_customers:
                continue

            num_sales = random.randint(100, 200)
            
            for _ in range(num_sales):
                salesperson = random.choice(regional_salespeople)
                customer = random.choice(regional_customers)
                product = random.choice(products)
                quantity = random.randint(1, 5)
                
                # Random date in last 18 months
                days_offset = random.randint(0, 540)
                sale_date = start_date + timedelta(days=days_offset)
                
                status = random.choices(
                    STATUS_CHOICES,
                    weights=[10, 70, 15, 5],  # mostly won
                    k=1
                )[0]

                Sale.objects.create(
                    customer=customer,
                    salesperson=salesperson,
                    product=product,
                    quantity=quantity,
                    date=sale_date,
                    status=status,
                    notes=fake.sentence(nb_words=8) if random.random() > 0.6 else "",
                )
                sales_created += 1

            self.stdout.write(f'  ✓ {num_sales} sales for {region}')

        # Ensure every customer has at least one sale
        self.stdout.write('Ensuring every customer has at least 1 sale...')
        for customer in customers:
            if not Sale.objects.filter(customer=customer).exists():
                # Assign a random sale
                salesperson = random.choice(salespeople)
                product = random.choice(products)
                Sale.objects.create(
                    customer=customer,
                    salesperson=salesperson,
                    product=product,
                    quantity=random.randint(1, 3),
                    date=date(2025, random.randint(1,5), random.randint(1,28)),
                    status='won',
                )
                sales_created += 1

        self.stdout.write(self.style.SUCCESS('✅ Data generation completed!'))
        self.stdout.write(self.style.SUCCESS(f'Total Sales created: {sales_created}'))
        self.stdout.write(self.style.SUCCESS(f'Total Sales in DB: {Sale.objects.count()}'))