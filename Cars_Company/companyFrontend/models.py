from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Admins(models.Model):
    admin_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50, unique=True)
    user_password = models.CharField(max_length=128)  # For hashed password
    is_manager = models.BooleanField(default=False)  # To identify managers

    class Meta:
        managed = True
        db_table = 'admins'

class Car(models.Model):
    car_id = models.AutoField(primary_key=True)
    car_type = models.CharField(max_length=50, blank=True, null=True)
    car_color = models.CharField(max_length=50, blank=True, null=True)
    car_name = models.CharField(max_length=50, blank=True, null=True)
    car_state = models.CharField(max_length=50, blank=True, null=True)
    year_manufacture = models.IntegerField(
    blank=True,
    null=True,
    validators=[
        MinValueValidator(1900),
        MaxValueValidator(2050)
    ]
    )
    car_metric = models.IntegerField(blank=True, null=True)
    SellingPrice = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    PurchasePrice = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    SellingDateTime = models.DateField(blank=True, null=True)
    PurchaseDateTime = models.DateField(blank=True, null=True)
    chassis = models.CharField(max_length=17, unique=True)

    class Meta:
        managed = True
        db_table = 'car'

class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    car = models.ForeignKey(Car, models.CASCADE, blank=True, null=True, db_column='car_id')

    class Meta:
        managed = True
        db_table = 'inventory'

class Financial(models.Model):
    record_id = models.AutoField(primary_key=True)
    car = models.OneToOneField(Car, models.CASCADE, db_column='car_id')  # Changed from ForeignKey to OneToOneField
    profits = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'financial'