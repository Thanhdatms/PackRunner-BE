from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema_view, extend_schema

estimate_location_parameters = [
    OpenApiParameter(
        name='origins',
        required=True,
        type=str,
        location=OpenApiParameter.QUERY,
        description='The starting point(s), format: "lat,lng" or multiple separated by "|".'
    ),
    OpenApiParameter(
        name='destinations',
        required=True,
        type=str,
        location=OpenApiParameter.QUERY,
        description='End point(s), format: "lat,lng" or multiple separated by "|".'
    )
]

estimate_location_responses = {
    200: OpenApiResponse(
        response={
            'duration': {'text': '10 mins', 'value': 600},
            'distance': {'text': '5.0 km', 'value': 5000},
            'status': 'OK'
        },
        description='Travel time and distance between origin and destination.'
    ),
    400: OpenApiResponse(description='Bad request, missing or invalid query parameters.'),
    500: OpenApiResponse(description='Internal server error or Google Maps API error.')
}

estimate_location = extend_schema_view(
    get=extend_schema(
        parameters=estimate_location_parameters,
        responses=estimate_location_responses,
        tags=['Location']
    )
)

estimate_routes_parameters = [
    OpenApiParameter(
        name='origin',
        required=True,
        type=str,
        location=OpenApiParameter.QUERY,
        description='The starting point, format: "lat,lng".'
    ),
    OpenApiParameter(
        name='destination',
        required=True,
        type=str,
        location=OpenApiParameter.QUERY,
        description='End point, format: "lat,lng".' 
    )
]
estimate_routes = extend_schema_view(
    get=extend_schema(
        parameters=estimate_routes_parameters,
        responses=estimate_location_responses,
        tags=['Location']
    )
)
