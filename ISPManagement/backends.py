# backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import WiFiProviders
from routeros_api import RouterOsApiPool


class WifiProviderBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, router_ip=None):
        try:
            provider = WiFiProviders.objects.get(
                mtk_username=username,
                mtk_password=password,
                router_ip=router_ip
            )
            return provider.user  
        except WiFiProviders.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class MikroTikAPI:
    def __init__(self, host, username, password, port=8728):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.api = None
        self.connection = None

    def connect(self):
        self.connection = RouterOsApiPool(
            host=self.host,
            username=self.username,
            password=self.password,
            port=self.port,
            plaintext_login=True
        )
        self.api = self.connection.get_api()

    def execute(self, path, command=None):
        resource = self.api.get_resource(path)
        if command:
            return resource.set(**command)
        else:
            return resource.get()

    def disconnect(self):
        if self.connection:
            self.connection.disconnect()


# Function to bind the router to your Django system
def bind_router_to_portal(provider):
    api = MikroTikAPI(provider.router_ip, provider.mtk_username, provider.mtk_password)
    try:
        api.connect()
        profiles = api.execute('/ip/hotspot/user-profile')

        for profile in profiles:
            if profile.get('name') == 'default':
                # Only update if not already set
                if profile.get('http-pap-login') != 'https://mybilling-27346a98580c.herokuapp.com/':
                    api.execute('/ip/hotspot/user-profile', {
                        '.id': profile['.id'],
                        'http-pap-login': 'https://mybilling-27346a98580c.herokuapp.com/',
                        'login-by': 'http-pap',
                    })
                break
        return True
    except Exception as e:
        print(f"Error binding router: {e}")
        return False
    finally:
        api.disconnect()


