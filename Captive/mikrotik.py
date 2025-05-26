from ISPManagement.models import WiFiProviders
from routeros_api import RouterOsApiPool
import datetime
from datetime import timedelta



class MikroTikAPI:
    def __init__(self,provider):
        self.api_pool = RouterOsApiPool(host=provider.router_ip, username=provider.mtk_username, password=provider.mtk_password,plaintext_login=True)
        self.api = self.api_pool.get_api()

    def add_hotspot_user(self, phone, duration, profile="default"):
        name = phone
        password = ""
        comment = f"Phone: {phone},Duration: {duration} min"

        hotspot_resource = self.api.get_resource('/ip/hotspot/user')
        hotspot_resource.add(
            name=name,
            password=password,
            comment = comment,
            profile = profile
        )
        if duration:
            scheduler = self.api.get_resource("/system/scheduler")
            remove = datetime.now()+timedelta(minutes=int(duration))
            scheduler.add(
                name = f"remove_{name}",
                start_time = remove.strftime("%H:%M:%S"),
                interval ="0s",
                on_event = f"/ppp/secret/remove[find/name=\"{name}\"]",
                comment = f"Auto-remove {name} after {duration} min"
            )
    def total_hotspot_users(self):
        hotspot_resource = self.api_pool.get_resource("ip/hotspot/active")
        hotspot_count = len(hotspot_resource.get())
        return hotspot_count


    def add_pppoe_user(self, password ,phone,duration,profile="default"):
        name =phone
        ppp_resource = self.api.get_resource('/ppp/secret')
        ppp_resource.add(
            name=name,
            password=password,
            profile=profile,
            service='pppoe',
        )
        if duration:
            scheduler = self.api.get_resource('/system/scheduler')
            remove_time = datetime.now() + timedelta(minutes=int(duration))
            scheduler.add(
                name=f"remove_{name}",
                start_time=remove_time.strftime("%H:%M:%S"),
                interval="0s",
                on_event=f"/ip/hotspot/user/remove [find name=\"{name}\"]",
                comment=f"Auto-remove {name} after {duration} min"
            )
    

    def total_pppoe_users(self):
        pppoe_resource = self.api_pool.get_resource("ppp/active")
        ppp_active = pppoe_resource.get()
        pppoe_count = len([u for u in ppp_active if u.get("service")=="pppoe"])
        return pppoe_count

    from datetime import datetime, timedelta

    def add_to_whitelist(self, ip, duration, mac=None, comment='Static client'):
        address_list = self.api_pool.get_resource('/ip/firewall/address-list')
        scheduler = self.api_pool.get_resource('/system/scheduler')

        # Add to firewall address list
        params = {
            'list': 'allowed-users',
            'address': ip,
            'comment': comment
        }
        if mac:
            params['mac-address'] = mac
        address_list.add(**params)

        # Parse duration (expects timedelta or minutes as int)
        if isinstance(duration, timedelta):
            remove_time = datetime.now() + duration
        elif isinstance(duration, int):
            remove_time = datetime.now() + timedelta(minutes=duration)
        else:
            raise ValueError("Duration must be a timedelta or integer (minutes)")

        # Format scheduler start time
        scheduler_start = remove_time.strftime("%H:%M:%S")
        scheduler_date = remove_time.strftime("%b/%d/%Y")  # MikroTik format: May/25/2025

        # Scheduler command to remove the user
        command = f"/ip/firewall/address-list/remove [find address={ip} list=allowed-users]"

        scheduler.add(
            name=f"remove_{ip.replace('.', '_')}",
            start_date=scheduler_date,
            start_time=scheduler_start,
            interval="0s",  # one-time
            on_event=command,
            comment=f"Auto-remove static IP {ip}"
        )


    def total_static_users(self):
        static_resource = self.api_pool.get_resource("ip/dhcp-server/lease")
        lease = static_resource.get()
        static_user_count = len([i for i in lease if i.get("dynamic")=="false" and i.get("status")=="bound"])
        return static_user_count

    def close(self):
        self.api_pool.disconnect()
