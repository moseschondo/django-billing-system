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
        profiles = api.execute('/ip/hotspot/user/profile')

        if not profiles:
            print("❌ No hotspot profiles found on the router.")
            return False

        print(f"🔍 Found {len(profiles)} hotspot profiles:")
        for p in profiles:
            print(p)

        updated = False
        new_url = 'https://www.tekpulsesoftwares.com/'

        for profile in profiles:
            profile_name = profile.get('name')
            profile_id = profile.get('.id') or profile.get('id')  # ✅ handles both cases

            if not profile_id:
                print(f"⚠️ Skipping profile '{profile_name}' — no ID found")
                continue

            current_login = profile.get('http-pap-login')

            if profile_name in ['hotspot1', 'default', 'Hotspot1']:
                if current_login != new_url:
                    print(f"🛠 Updating profile '{profile_name}' (ID: {profile_id})...")
                    api.execute('/ip/hotspot/user/profile', {
                        '.id': profile_id,
                        'http-pap-login': new_url,
                        'login-by': 'http-pap',
                    })
                    print(f"✅ Updated login URL for profile: {profile_name}")
                else:
                    print(f"ℹ️ Login URL for {profile_name} already correct.")
                updated = True
                break

        if not updated:
            print("⚠️ No matching hotspot profile ('hotspot1' or 'default') found.")
            return False

        return True

    except Exception as e:
        print(f"[Router Binding Error] {e}")
        return False
    finally:
        api.disconnect()






