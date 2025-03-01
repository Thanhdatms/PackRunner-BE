from rest_framework.response import Response

def success_response(data, message="Successfully"):
    return Response({
        "message": message,
        "data": data
    }, status=200)

def fail_response(error, status_code=400):
    return Response({
        "status": "error",
        "message": str(error)
    }, status=status_code)