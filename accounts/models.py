from django.contrib.auth.models import AbstractUser
from django.db import models
from restaurants.models import Restaurant


class CustomUser(AbstractUser):
    MANAGER = "manager"
    GM = "gm"
    DM = "dm"
    SUPERUSER = "superuser"

    ROLE_CHOICES = [
        (MANAGER, "Manager"),
        (GM, "General Manager"),
        (DM, "District Manager"),
        (SUPERUSER, "Superuser"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MANAGER)

    # For managers and GMs, assign one restaurant.
    restaurant = models.ForeignKey(
        Restaurant,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )

    # For DM role (and optionally superuser if needed), allow multiple restaurants.
    restaurants = models.ManyToManyField(
        Restaurant, blank=True, related_name="district_managers"
    )

    def __str__(self):
        return self.username
