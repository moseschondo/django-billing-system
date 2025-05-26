from django import forms 
from django.forms import models
from django.contrib.auth.models import User
from Captive.models import WiFiPlan

class PaymentForm(forms.Form):
  plan = forms.ModelChoiceField(queryset=WiFiPlan.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}), empty_label=None)
  connect = forms.CharField(max_length=20) 

   


