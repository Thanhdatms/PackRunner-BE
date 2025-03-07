import hashlib

def generate_shipment_code(order_id):
    # Combine the order ID with a prefix to make the code unique
    raw_code = f"SHIP-{order_id}"
    
    # Use a hash function to generate a fixed-length code from the order ID
    hash_object = hashlib.sha256(raw_code.encode())  # SHA-256 hashing for uniqueness
    shipment_code = hash_object.hexdigest()[:6]  # Use the first 10 characters of the hash
    
    return shipment_code