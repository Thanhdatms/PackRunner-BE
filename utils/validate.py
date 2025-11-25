import hashlib

def generate_shipment_code(order_id):
    raw_code = f"SHIP-{order_id}"
    
    hash_object = hashlib.sha256(raw_code.encode())
    shipment_code = hash_object.hexdigest()[:6]
    
    return shipment_code