from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """Extra bakery-customer information attached to Django's built-in User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_admin_staff = models.BooleanField(
        default=False,
        help_text="Marks this account as bakery staff/administrator for dashboard access."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
