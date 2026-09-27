from django.core.management.base import BaseCommand
from django.db.models import Q, F
from django.db import connection, reset_queries
from django.utils import timezone
from datetime import timedelta
from restaurants.models import Restaurant, Sale

class Command(BaseCommand):
    help = 'Demonstrates complex queries using Q objects, lookups, and regex.'

    def handle(self, *args, **kwargs):
        self.populate_data()
        
        # Enable query logging in terminal
        from django.conf import settings
        settings.DEBUG = True 
        reset_queries()

        thirty_days_ago = timezone.now().date() - timedelta(days=30)

        # Encapsulated Q Objects
        italian_mexican_q = Q(restaurant_type='Italian') | Q(restaurant_type='Mexican')
        recently_opened_q = Q(date_opened__gte=thirty_days_ago)
        not_recently_opened_q = ~recently_opened_q
        name_has_digit_q = Q(restaurant__name__regex=r'\d+')
        profitable_q = Q(income__gt=F('expenditure'))

        self.stdout.write(self.style.SUCCESS('\n--- 1a. Italian OR Mexican ---'))
        print(Restaurant.objects.filter(italian_mexican_q))

        self.stdout.write(self.style.SUCCESS('\n--- 1b. NOT opened in last 30 days ---'))
        print(Restaurant.objects.filter(not_recently_opened_q))

        self.stdout.write(self.style.SUCCESS('\n--- 1c. Italian/Mexican OR opened in last 30 days ---'))
        combined_q = italian_mexican_q | recently_opened_q
        print(Restaurant.objects.filter(combined_q))

        self.stdout.write(self.style.SUCCESS('\n--- 2a. Contains "grill" (case-insensitive) ---'))
        print(Restaurant.objects.filter(name__icontains='grill'))

        self.stdout.write(self.style.SUCCESS('\n--- 2b. Ends with "Cafe" ---'))
        print(Restaurant.objects.filter(name__endswith='Cafe'))

        self.stdout.write(self.style.SUCCESS('\n--- 3a. Name contains one or more digits (Regex) ---'))
        print(Restaurant.objects.filter(name__regex=r'\d+'))

        self.stdout.write(self.style.SUCCESS('\n--- 3b. Income > Expenditure OR Restaurant name has digit ---'))
        # Using select_related for performance optimization
        sales = Sale.objects.select_related('restaurant').filter(profitable_q | name_has_digit_q)
        print(sales)

        self.stdout.write(self.style.SUCCESS('\n--- SQL Queries Executed ---'))
        for query in connection.queries:
            print(query['sql'])

    def populate_data(self):
        if not Restaurant.objects.exists():
            r1 = Restaurant.objects.create(name="Luigi's", restaurant_type="Italian", date_opened=timezone.now().date() - timedelta(days=10))
            r2 = Restaurant.objects.create(name="Taco Grill 99", restaurant_type="Mexican", date_opened=timezone.now().date() - timedelta(days=40))
            r3 = Restaurant.objects.create(name="Downtown Cafe", restaurant_type="Cafe", date_opened=timezone.now().date() - timedelta(days=100))
            
            Sale.objects.create(restaurant=r1, income=5000, expenditure=6000)
            Sale.objects.create(restaurant=r2, income=8000, expenditure=3000)
            Sale.objects.create(restaurant=r3, income=4000, expenditure=2000)