from django.shortcuts import render
import requests
import os
from rest_framework.views import APIView
from utils.response import success_response, fail_response

# Create your views here.

class EstimateLocationView(APIView):
    def get(self, request):
        try:
            # Extract latitude and longitude from the request
            origins = request.query_params.get('origins')
            destinations = request.query_params.get('destinations')
            if not origins or not destinations:
                return fail_response("Origins and destinations are required", status_code=400)  
            
            url_template = os.environ.get('GOOGLE_MAPS_ESTIMATE_URL')
            api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
            url = url_template.format(destinations=destinations, origins=origins, key=api_key)
            data = requests.get(url).json()

            if data['status'] != 'OK':
                return fail_response("Unable to fetch directions", status_code=400)
            return success_response(data['rows'][0]['elements'][0], message="Estimated time of arrival")
        except requests.RequestException as e:
            return fail_response(f"Request failed: {str(e)}", status_code=500)
        except KeyError:
            return fail_response("Invalid response from Google Maps API", status_code=500)
        except Exception as err:
            return fail_response({"error": str(err)}, status_code=500)
        
class EstimateRoutes(APIView):
    def get(self, request):
        try:
            # Extract latitude and longitude from the request
            origin = request.query_params.get('origin')
            destination = request.query_params.get('destination')
            
            if not origin or not destination:
                return fail_response("Origin and destination are required", status_code=400)    
            
            url_template = os.environ.get('GOOGLE_MAPS_ROUTE_URL')
            api_key = os.environ.get('GOOGLE_MAPS_API_KEY')

            url = url_template.format(origin=origin, destination=destination, key=api_key)
            data = requests.get(url).json()

            if data['status'] != 'OK':
                return fail_response("Unable to fetch directions", status_code=400)
            return success_response(data['routes'][0]['legs'][0], message="Estimated time of arrival")
        except requests.RequestException as e:
            return fail_response(f"Request failed: {str(e)}", status_code=500)
        except KeyError:
            return fail_response("Invalid response from Google Maps API", status_code=500)
        except Exception as err:
            return fail_response({"error": str(err)}, status_code=500)