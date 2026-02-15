# models.py

from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)  # Increased for future hashing
    number = models.BigIntegerField()

    def __str__(self):
        return self.email


class Meeting(models.Model):
    room_name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(Customer, on_delete=models.CASCADE)
    participants = models.ManyToManyField(Customer, related_name="meetings")

    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room_name} ({'Active' if self.is_active else 'Ended'})"