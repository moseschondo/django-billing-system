from django import forms
from ISPManagement.models import WiFiProviders, AccessCode
from django.contrib.auth.models import User


class Customer_reg_form(forms.ModelForm):
    router_ip = forms.GenericIPAddressField(label="Router IP Address:")
    mtk_username = forms.CharField(label="Mikrotik Username",max_length=50)
    mtk_password = forms.CharField(label="Mikrotik Password ",widget=forms.PasswordInput())
    customer_phone = forms.CharField(label="Phone Number",max_length=13)
    customer_number = forms.CharField(label="Till Number")
    mpesacode = forms.CharField(label="M-Pesa Code",max_length=20)

    class Meta:
        model = WiFiProviders
        fields = ["router_ip", "customer_phone","customer_number","mtk_username", "mtk_password"]

    def clean_mtk_username(self):
        mikrtotik_username = self.cleaned_data.get("mtk_username")
        if WiFiProviders.objects.filter(mtk_username=mikrtotik_username).exists():
            raise forms.ValidationError("The Mikrotik username already exists.")
        return mikrtotik_username
    
    def clean(self):
        cleaned_data = super().clean()
        mtk_username = cleaned_data.get("mtk_username")
        if mtk_username and User.objects.filter(username=mtk_username).exists():
            self.add_error("mtk_username", "This Mikrotik username is already registered as a system user.")

        

    def clean_router_ip(self):
        router_ip = self.cleaned_data.get("router_ip")
        if WiFiProviders.objects.filter(router_ip=router_ip).exists():
            raise forms.ValidationError("The router IP already exists.")
        return router_ip

    def clean_customer_phone(self):
        customer_phone = self.cleaned_data.get("customer_phone")
        if WiFiProviders.objects.filter(customer_phone=customer_phone).exists():
            raise forms.ValidationError("The phone number already exists.")
        return customer_phone

    def clean_customer_number(self):
        customer_number = self.cleaned_data.get("customer_number")
        if WiFiProviders.objects.filter(customer_number=customer_number).exists():
            raise forms.ValidationError("The Paybill/Till number already exists.")
        return customer_number


class login_form(forms.Form):
    mtk_username = forms.CharField(label="Username",max_length=50)
    mtk_password = forms.CharField(label="Password", widget=forms.PasswordInput())

 

def generate_access_code(self):
    selected_plan = self.cleaned_data['plan']
    access_code = AccessCode(plan=selected_plan)
    access_code.save()
    return access_code


class StaticForm(forms.Form):
    ip_address = forms.GenericIPAddressField(protocol="both", required=True, label="IP Address")
    subnet_mask = forms.CharField(label="Subnet Mask")
    gateway = forms.CharField(label="Gateway")

    start_datetime = forms.DateField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Start Date"
    )
    end_datetime = forms.DateField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="End Date"
    )
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_datetime")
        end = cleaned_data.get("end_datetime")

        if start and end and start >= end:
            raise forms.ValidationError("End date and time must be after start date and time.")


class PPPoEForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
