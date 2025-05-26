from django.db import models
from django.utils import timezone

class Subscribers(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    access_code = models.OneToOneField("ISPManagement.AccessCode", on_delete=models.SET_NULL, null=True, blank=True)
    connected_at = models.DateTimeField(null=True, blank=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    is_connected = models.BooleanField(default=False)
    wifi_plan = models.ForeignKey("ISPManagement.WiFiPlan", on_delete=models.SET_NULL, null=True, blank=True)
    wifi_provider = models.ForeignKey("ISPManagement.WiFiProviders", on_delete=models.CASCADE,default=0)
    mac_address = models.CharField(max_length=50, null=True, blank=True)



class Transaction(models.Model):
    phone_number = models.CharField(max_length=15)
    plan = models.ForeignKey("ISPManagement.WiFiPlan",on_delete=models.SET_NULL,null=True)
    mpesa_code = models.CharField(max_length=10,unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    session_id = models.CharField(max_length=100)
    checkout_id = models.CharField(max_length=100, default="N/A")
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("paid", "Paid")])

    def __str__(self):
        return f"{self.mpesa_code} -{self.phone_number} -{self.plan}"


