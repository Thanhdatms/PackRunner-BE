import base64

def generate_shipment_code(code):

    encoded = base64.b64encode(code.encode())  
    return encoded