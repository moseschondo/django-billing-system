from django.urls import path
from Captive.views import portal,payment,payment_view,payment_callback,stk_status_view
from ISPManagement.views import provider_login,register_provider,generate_access_code,force_logout

urlpatterns = [
    path("portal/", portal, name="portal"),
    path("payment/",payment, name="payment_1"),
    path("paying/", payment_view, name="paid"),
    path('payment-callback/', payment_callback, name='payment_callback'),
    path("stk-status/",stk_status_view,name="stk_status"),
    path("login/",provider_login, name="login"),
    path("register/", register_provider, name="register"),
    path("generate accesscode/", generate_access_code, name="generating"),
    path('force-logout/', force_logout, name='force_logout'),
]