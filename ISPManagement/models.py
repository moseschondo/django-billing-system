from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from Captive.models import Transaction
import secrets
import string

# Create your models here.
class WiFiProviders(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    router_ip = models.GenericIPAddressField(protocol="both", unique=True)
    customer_phone = models.CharField(max_length=15, unique=True,default=0)
    customer_number = models.IntegerField(default=0)
    mtk_username = models.CharField(max_length=50)
    mtk_password = models.CharField(max_length=100, unique=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.router_ip} {self.mtk_username} {self.mtk_password} {self.customer_number} {self.customer_phone}"
    
class WiFiPlan(models.Model):
    name = models.CharField(max_length=50)
    wifiprovider = models.ForeignKey(WiFiProviders, null=True,on_delete=models.CASCADE)
    price = models.IntegerField()
    planamount = models.ForeignKey(Transaction,null=True, on_delete=models.CASCADE)
    duration = models.IntegerField(help_text="Duration in minutes")

    def __str__(self):
        return f"{self.name}{self.duration} {self.price} KES"

class AccessCode(models.Model):
    subscriber_phone = models.CharField(max_length=20, null=True, blank=True, unique=False)# Allow empty for test codes
    code = models.CharField(max_length=12, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Optional for test codes without duration
    is_connected = models.BooleanField(default=False)
    last_connected = models.DateTimeField(null=True, blank=True)
    plan = models.ForeignKey('WiFiPlan', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Code {self.code} for {self.subscriber_phone or 'Test'} (Expires: {self.expires_at or 'N/A'}, Connected: {self.is_connected})"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        if not self.expires_at:
            self.expires_at = self.calculate_expiry()
        super().save(*args, **kwargs)

    def generate_unique_code(self, length=12):
        """Generate a secure, alphanumeric, and unique code."""
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(secrets.choice(characters) for _ in range(length))
            if not AccessCode.objects.filter(code=code).exists():
                return code

    def calculate_expiry(self, custom_duration=None):
        """Calculate expiry based on plan or custom test duration."""
        if self.plan:
            return timezone.now() + timezone.timedelta(minutes=self.plan.duration)
        if custom_duration:
            return timezone.now() + timezone.timedelta(minutes=custom_duration)
        return None  # For test codes with no expiry



    def calculate_expiry(self):
        return timezone.now() + timezone.timedelta(hours=self.plan.duration_hours) #Calculate from the plan

    def is_expired(self):
        return self.expires_at < timezone.now()





class StaticClient(models.Model):
    ip_address = models.GenericIPAddressField()
    subnet_mask = models.CharField(max_length=20)
    gateway = models.CharField(max_length=20)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address}{self.subnet_mask}{self.gateway}{self.start_datetime}{self.end_datetime}"

class PPPoEClients(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.username} {self.password}"
