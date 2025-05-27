from django.shortcuts import render,redirect
import requests, base64, json
from datetime import datetime
from Captive.models import Transaction
from ISPManagement.models import WiFiProviders, WiFiPlan
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import routeros_api
from Captive.mikrotik import MikroTikAPI
from django.contrib.auth.models import User


def portal(request):
    plans = WiFiPlan.objects.all()
    return render(request, "Captive/index.html", {"plans": plans})

# Phone number formatting and validation
def format_phone_number(phone):
    """Convert phone numbers to the required M-Pesa format (2547XXXXXXXX)."""
    if not phone:
        return None
    phone = phone.strip().replace(" ", "").replace("-", "")  # Remove spaces and dashes
    if phone.startswith("07") or phone.startswith("01"):
        return "254" + phone[1:]
    elif phone.startswith("+254"):
        return phone[1:]  # Remove the '+' if present
    elif phone.startswith("254"):
        return phone  # Already in correct format
    else:
        return None  # Invalid phone format

# Handles and renders index.html
def payment(request):
    global plan_duration
    if request.method == "POST":
        plan_info = request.POST.get("plan_info")
        if plan_info:
            plan_price, plan_duration = plan_info.split("|")
            return render(request,"Captive/payment.html",{"plan_price": plan_price,"plan_duration": plan_duration})
        else:
            return render(request,"Captive/index.html")
        
def connect_subscriber(provider, phone):
    """
    1. Connect to the provider’s router
    2. Create a hotspot user with a time‑limited profile
    """
    # 1) connect
    connection =routeros_api.RouterOsApiPool(
        host=provider.router_ip,
        username=provider.mtk_username,
        password=provider.mtk_password,
        plaintext_login=True
    )
    api = connection.get_api()

    # 2) ensure you have a hotspot profile that enforces the right timeout
    # You may need to create one named, say, "temp-<minutes>"
    profiles = api.get_resource('/ip/hotspot/user/profile').get()
    profile_name = f"temp-{plan_duration} minutes"
    if not any(p['name'] == profile_name for p in profiles):
        api.get_resource('/ip/hotspot/user/profile').add(
            name=profile_name,
            # up/down limits, session-timeout, etc:
            session_timeout=f"{plan_duration}m",
        )

    # 3) add the user
    api.get_resource('/ip/hotspot/user').add(
        name=phone,           
        password=phone,               
        profile=profile_name,          
        server="hotspot1",       
    )
    connection.disconnect()
    
def get_provider_details(request):
    try:
        provider = WiFiProviders.objects.get(user=request.user)
        providernumber = provider.customer_phone
        mpesa_code = provider.customer_number
        return providernumber, mpesa_code
    except WiFiProviders.DoesNotExist:
        return None, None


CONSUMER_KEY = "tO3GA5F4KjUDbN1HZiGsGMyj9WVy8NeOhs5qeIX76GXmt9go"
CONSUMER_SECRET = "oa7I0Z2FLYYq3WDpgj5gMDVyylhQYIAcS8wA856OoGanWbuLGHtA1rztBzovQWAR"
Head_office_number = "5496346" # Head Office number
MPESA_PASSKEY = "5d8526b4edb967f9f2e2dd9577f2ea4024edb5414e09735e52deec84a800a992"
CALLBACK_URL = "https://mybilling-27346a98580c.herokuapp.com/"

def generate_access_token():
    try:
        credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }
        response = requests.get("https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
            headers=headers,
        ).json()

        if "access_token" in response:
            return response["access_token"]
        else:
            raise Exception("Access token missing in response.")

    except requests.RequestException as e:
        raise Exception(f"Failed to connect to M-Pesa: {str(e)}")

# Initiate STK Push and handle response
def initiate_stk_push(request,phone, amount):
    providernumber, mpesa_code = get_provider_details(request)
    
    try:
        token = generate_access_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        stk_password = base64.b64encode(
            (Head_office_number + MPESA_PASSKEY + timestamp).encode()
        ).decode()

        request_body = {
            "BusinessShortCode": Head_office_number,
            "Password": stk_password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerBuyGoodsOnline",
            "Amount": amount,
            "PartyA": providernumber, #Recipient phone number(One providers phone number!!)
            "PartyB": mpesa_code,
            "PhoneNumber": phone,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": "account",
            "TransactionDesc": "Payment for internet",
        }

        response = requests.post("https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=request_body,
            headers=headers,
        ).json()

        return response

    except Exception as e:
        raise e

# Payment View
def payment_view(request):
    global planid
    if request.method == "POST":
        phone = format_phone_number(request.POST.get("phone_number"))
        amount = request.POST.get("planamount")
        planid = request.POST.get("planduration")

        try:
            response = initiate_stk_push(request,phone, amount)
            
            if response.get("ResponseCode") == "0":
                checkout_request_id = response["CheckoutRequestID"]
                Transaction.objects.create(
                    phone_number=phone,
                    amount=amount,
                    status="Pending",
                    checkout_id=checkout_request_id,
                )

                return render(request, "Captive/pending.html", {"checkout_request_id": checkout_request_id})
            else:
                error_message = response.get("errorMessage", "Failed to send STK push. Please try again.")
                return render(request, "Captive/payment.html", {"error_message": error_message})
        except WiFiPlan.DoesNotExist:
            return render(request, "Captive/payment.html", {"error_message": "Invalid plan selected."})
        except Exception as e:
            return render(request, "Captive/payment.html", {"error_message": f"An unexpected error occurred: {str(e)}"})

    return render(request, "Captive/payment.html")

# Query STK Push status
def query_stk_push(checkout_request_id):
    print("Quering...")
    try:
        token = generate_access_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            (Head_office_number + MPESA_PASSKEY + timestamp).encode()
        ).decode()

        request_body = {
            "BusinessShortCode": Head_office_number,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        response = requests.post("https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query",
            json=request_body,
            headers=headers,
        )
        print(response.json())
        return response.json()

    except requests.RequestException as e:
        print(f"Error querying STK status: {str(e)}")
        return {"error": str(e)}

# View to query the STK status and return it to the frontend
def stk_status_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        checkout_request_id = data.get('checkout_request_id')

        # Query STK push status
        response = query_stk_push(checkout_request_id)
        result_code = response.get("ResultCode")

        if result_code == "0":
            try:

                txn = Transaction.objects.get(checkout_request_id=checkout_request_id)
                txn.status = 'Paid'
                txn.mpesa_code = response.get("MpesaReceiptNumber")
                txn.save()
                connect_subscriber(txn.phone_number,planid)

                return JsonResponse({"status": response})
            except Transaction.DoesNotExist:
                return JsonResponse({"error": "Transaction does not exist!"})
            except WiFiProviders.DoesNotExist:
                return JsonResponse({"error": "Provider not found!"})
            except Exception as e:
                return JsonResponse({"error": str(e)})
        # Payment failed or still pending
        return JsonResponse({"status": response})
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt  # To allow POST requests from external sources like M-Pesa
def payment_callback(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests are allowed")

    try:
        callback_data = json.loads(request.body)
        result_code = callback_data["Body"]["stkCallback"]["ResultCode"]

        if result_code == 0:
            checkout_id = callback_data["Body"]["stkCallback"]["CheckoutRequestID"]
            metadata = callback_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]

            amount = next(item["Value"] for item in metadata if item["Name"] == "Amount")
            mpesa_code = next(item["Value"] for item in metadata if item["Name"] == "MpesaReceiptNumber")
            phone = next(item["Value"] for item in metadata if item["Name"] == "PhoneNumber")

           

            mikrotik = MikroTikAPI()
            mikrotik.add_hotspot_user(phone,duration=planid)

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Payment successful"})

        return JsonResponse({"ResultCode": result_code, "ResultDesc": "Payment failed"})

    except (json.JSONDecodeError, KeyError, Transaction.DoesNotExist) as e:
        return HttpResponseBadRequest(f"Invalid request: {str(e)}")






