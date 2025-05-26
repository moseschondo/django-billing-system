from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from ISPManagement.models import WiFiProviders,StaticClient
from ISPManagement.forms import Customer_reg_form,login_form,StaticForm, PPPoEForm
from django.contrib import messages
import random, string
from ISPManagement.backends import bind_router_to_portal
from Captive.mikrotik import MikroTikAPI
from django.contrib.auth.decorators import login_required




def register_provider(request):
    if request.method == "POST":
        form = Customer_reg_form(request.POST)
        if form.is_valid():
            # Create Django User using MikroTik credentials
            user = User.objects.create_user(
                username=form.cleaned_data["mtk_username"],
                password=form.cleaned_data["mtk_password"],
            )

            # Save provider details
            provider = WiFiProviders.objects.create(
                user=user,
                customer_phone=form.cleaned_data["customer_phone"],
                customer_number=form.cleaned_data["customer_number"],
                router_ip=form.cleaned_data["router_ip"],
                mtk_username=form.cleaned_data["mtk_username"],
                mtk_password=form.cleaned_data["mtk_password"]
            )
            provider.save()
            success = bind_router_to_portal(provider)

            if not success:
                # Optional: Show error if binding fails
                return render(request, "ISPManagement/register.html", {
                    "form": form,
                    "error": "Registered, but failed to bind router. Please check router credentials and try again."
                })

    else:
        form = Customer_reg_form()
    return render(request, "ISPManagement/register.html", {"form": form})




def provider_login(request):
    form = login_form()
    if request.method == "POST":
        form = login_form(request.POST)
        if form.is_valid():
            mtk_username = form.cleaned_data["mtk_username"]
            mtk_password = form.cleaned_data["mtk_password"]

            # Use Django's custom authentication backend
            user = authenticate(
                request,
                username=mtk_username,
                password=mtk_password
            )

            if user is not None:
                login(request, user)
                return redirect("dashboard") 
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, "ISPManagement/login.html", {"form": form})

@login_required
def finance(request):
    provider_details = WiFiProviders.objects.all(user = request.user)
    return render(request, 'ISPManagement/finance.html/', {'provider_details': provider_details})

@login_required
def generate_access_code(request):
    if request.method == 'POST':
        code_length = 7
        characters = string.ascii_letters + string.digits
        access_code = ''.join(random.choices(characters, k=code_length)).upper()
        return render(request, 'ISPManagement/accescode.html', {'code': access_code})
    return render(request, 'ISPManagement/accescode.html')


def force_logout(request):
    logout(request)
    return redirect('/admin/')

@login_required
def dashboard(request):
    static_form = StaticForm()
    pppoe_form = PPPoEForm()

    try:
        provider = WiFiProviders.objects.get(user=request.user)
        counter = MikroTikAPI(provider)  # move inside try

        active_hotspot_users = counter.total_hotspot_users()
        active_static_users = counter.total_static_users()
        active_pppoe_users = counter.total_pppoe_users()
        counter.close()

    except Exception as e:
        print(f"MikroTik connection failed: {e}")
        active_hotspot_users = active_static_users = active_pppoe_users = 0
        total_users = 0

        # Optional: show a warning in the UI using Django messages
        messages.error(request, "Error check if your router is active")
        return redirect("login")


    total_users = active_pppoe_users + active_static_users + active_hotspot_users

    return render(request, 'ISPManagement/clients.html', {
        'active_hotspot_users': active_hotspot_users,
        'active_static_users': active_static_users,
        'active_pppoe_users': active_pppoe_users,
        'total_users': total_users,
        'static_form': static_form,
        'pppoe_form': pppoe_form,
    })

@login_required
def features(request):
    return render(request,"ISPManagement/features.html/")

@login_required
def routers(request):
    return render(request,"ISPManagement/routers.html")


def register_static_client(request):
    if request.method == 'POST':
        form = StaticForm(request.POST)
        if form.is_valid():
            # Save to DB
            client = StaticClient.objects.create(
                ip_address=form.cleaned_data['ip_address'],
                subnet_mask=form.cleaned_data['subnet_mask'],
                gateway=form.cleaned_data['gateway'],
                start_datetime=form.cleaned_data['start_datetime'],
                end_datetime=form.cleaned_data['end_datetime'],
            )

            # Calculate duration in minutes or timedelta
            duration = client.end_datetime - client.start_datetime

            # Add to MikroTik whitelist with auto-remove scheduler
            mikrotik = MikroTikAPI()
            mikrotik.add_to_whitelist(
                ip=client.ip_address,
                duration=duration,
                comment=f"Static client until {client.end_datetime}"
            )
            mikrotik.close()

            return redirect('dashboard')
    else:
        form = StaticForm()

    return render(request, 'ISPManagement/register_static.html', {'form': form})

        
def register_pppoe_client(request):
    if request.method == "POST":
        form = PPPoEForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Register the user with MikroTik
            api = MikroTikAPI()
            api.add_pppoe_user(name=username, password=password, profile="default")
            api.close()

            return redirect("dashboard/")
    else:
        form = PPPoEForm()

    return render(request, "ISPManagement/clients.html", {"form": form})



