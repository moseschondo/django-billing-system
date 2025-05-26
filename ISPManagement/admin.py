from django.contrib import admin
from Captive.models import Transaction,Subscribers
from .models import WiFiProviders,WiFiPlan,PPPoEClients,StaticClient

# Register your models here.

@admin.register(WiFiProviders)

class WiFiProvidersAdmin(admin.ModelAdmin):
    list_display = ['user', 'router_ip', 'customer_phone', 'customer_number', 'mtk_username', 'mtk_password', 'created_at']
    list_filter = ['router_ip']

@admin.register(WiFiPlan)
class WiFiPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration']

@admin.register(PPPoEClients)
class PPPoEClientAdmin(admin.ModelAdmin):
    list_display = ['username']

@admin.register(StaticClient)
class StaticClientAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'subnet_mask', 'gateway', 'start_datetime', 'end_datetime']

@admin.register(Subscribers)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['phone_number','mac_address','wifi_plan']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['phone_number','mpesa_code','plan','status']

