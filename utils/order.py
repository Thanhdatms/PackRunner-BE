import os
import requests

def calculate_distance(origin, destination):
        try:
            url_template = os.environ.get('GOOGLE_MAPS_ESTIMATE_URL')
            api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
            url = url_template.format(destinations=destination, origins=origin, key=api_key)
            data = requests.get(url).json()
            print(data)
            distance_meters = data['rows'][0]['elements'][0]['distance']['value']
            return distance_meters / 1000
            
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return 0 
        
def calculate_total_price(shipments_data):
    total_price = 0
    weight = shipments_data.get('weight', 0)
    size = shipments_data.get('size', 'M')
    if size == 'S':
        total_price += weight * 10000
    elif size == 'M':
        total_price += weight * 20000
    elif size == 'L':
        total_price += weight * 30000
    elif size == 'XL':
        total_price += weight * 40000

    receiver_address = shipments_data.get('receiver_address', '')
    receiver_province = shipments_data.get('receiver_province', '')
    receiver_district = shipments_data.get('receiver_district', '')
    receiver_ward = shipments_data.get('receiver_ward', '')

    sender_address = shipments_data.get('sender_address', '')
    sender_province = shipments_data.get('sender_province', '')
    sender_district = shipments_data.get('sender_district', '')
    sender_ward = shipments_data.get('sender_ward', '')

    origin = f"{sender_address}, {sender_province}, {sender_district}, {sender_ward}"
    destination = f"{receiver_address}, {receiver_province}, {receiver_district}, {receiver_ward}"

    distance = calculate_distance(origin, destination)
    total_price += distance * 10000

    return total_price