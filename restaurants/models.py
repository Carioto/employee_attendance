from django.db import models


class Restaurant(models.Model):
    # Since we reference a class, the __init__ is controed by Django
    name = models.CharField(max_length=255)
    storeid = models.CharField(max_length=8)
    address = models.CharField(max_length=255, blank=True, null=True)
    # Field for the assigned GM (optional)
    gm = models.ForeignKey(
        "accounts.CustomUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"role": "gm"},
        related_name="managed_restaurant",
    )

    def __str__(self):
        return self.name


class Employee(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="employees"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # Optionally, add additional fields like contact info, position, etc.

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
