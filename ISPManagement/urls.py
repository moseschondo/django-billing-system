from django.urls import path
from . import views

urlpatterns = [
    path("",views.provider_login, name="login"),
    path("finance/", views.finance, name="finance"),
    path("register/", views.register_provider, name="register"),
    path("generate accesscode/", views.generate_access_code, name="generating"),
    path('force-logout/', views.force_logout, name='force_logout'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("settings/", views.settings, name="settings"),
    path("paymentsettings/",views.paymentsettings,name="paymentsettings"),
]