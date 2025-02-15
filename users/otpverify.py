import http.client
import json

def sendSmSOTP(phone_number, otp):
    try:
        conn = http.client.HTTPSConnection("api.infobip.com")
        payload = json.dumps({
            "messages": [
                {
                    "destinations": [{"to": f"{phone_number}"}],
                    "from": "447491163443",
                    "text": f"Your PackRunner OTP code: {otp}. This will expire in 3 minutes."
                }
            ]
        })
        
        headers = {
            'Authorization': 'App 83126cd2e153a71ecf3307361113ba91-f32747db-7e56-4ded-9012-3af06b0b630c',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        conn.request("POST", "/sms/2/text/advanced", payload, headers)
        
        response = conn.getresponse()
        print(f"Response status: {response.status}")
        print(f"Response body: {response.read().decode()}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
