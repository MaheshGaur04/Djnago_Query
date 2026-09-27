from django.db import models

class Restaurant(models.Model):
    TYPE_CHOICES = [
        ('Italian', 'Italian'),
        ('Mexican', 'Mexican'),
        ('American', 'American'),
        ('Cafe', 'Cafe'),
    ]
    name = models.CharField(max_length=255)
    restaurant_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    date_opened = models.DateField()

    def __str__(self):
        return self.name

class Sale(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    expenditure = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Sale for {self.restaurant.name}"
