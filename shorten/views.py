from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import URL
from .serializers import URLSerializer
from django.http import HttpResponseRedirect



@swagger_auto_schema(
    method='post',
    operation_description="Shorten a given URL for the authenticated user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'long_url': openapi.Schema(type=openapi.TYPE_STRING, description="The URL to be shortened", example="https://www.example.com")
        },
        required=['long_url']
    ),
    responses={
        201: openapi.Response(
            description="URL was successfully created.",
            schema=URLSerializer
        ),
        400: openapi.Response(
            description="Long URL is required.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Long URL is required")
                }
            )
        ),
        500: openapi.Response(
            description="An internal error occurred.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="An unexpected error occurred.")
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def shorten_url(request):
    """
    Shorten a given URL for the authenticated user.
    """
    try:
        long_url = request.data.get('long_url')
        if not long_url:
            return Response({"status": "error","message": "Long URL is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new URL record
        url = URL.objects.create(user=request.user, long_url=long_url)

        return Response({"status": "success", "message": "Url record was created", "data": URLSerializer(url).data}, status=status.HTTP_201_CREATED)

        
    except Exception as e: 
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    methods=['GET'],  # Explicitly specify the method to apply the decorator to
    operation_description="Fetch all shortened URLs for the authenticated user.",
    responses={
        200: openapi.Response(
            description="URLs were successfully retrieved.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Urls were successfully retrieved"),
                    'data': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'long_url': openapi.Schema(type=openapi.TYPE_STRING, example="https://www.example.com"),
                                'shortened_url': openapi.Schema(type=openapi.TYPE_STRING, example="https://short.ly/abcd1234")
                            }
                        ),
                        description="List of shortened URLs for the authenticated user"
                    )
                }
            )
        ),
        500: openapi.Response(
            description="An internal error occurred.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="An unexpected error occurred.")
                }
            )
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_urls(request):
    """
    Fetch all shortened URLs for the authenticated user.
    """
    try:
        urls = URL.objects.filter(user=request.user)
        # Assuming you have a serializer named URLSerializer to serialize the URLs
        serializer = URLSerializer(urls, many=True)
        return Response({"status": "success", "message": "Urls were successfully retrieved", "data": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    



@swagger_auto_schema(
    methods=['GET'],  # Explicitly specify the method to apply the decorator to
    operation_description="Fetch analytics for a specific shortened URL.",
    manual_parameters=[
        openapi.Parameter(
            'shortUrl',  # The parameter name in the URL
            openapi.IN_PATH,  # This is a path parameter
            description="The shortened URL code to fetch analytics for",
            type=openapi.TYPE_STRING,
            required=True,
            example="abcd1234"
        )
    ],
    responses={
        200: openapi.Response(
            description="Analytics for the shortened URL were successfully retrieved.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'short_code': openapi.Schema(type=openapi.TYPE_STRING, example="abcd1234"),
                            'long_url': openapi.Schema(type=openapi.TYPE_STRING, example="https://www.example.com"),
                            'shortened_url': openapi.Schema(type=openapi.TYPE_STRING, example="https://short.ly/abcd1234"),
                            # Add other fields from URLSerializer as needed
                        }
                    ),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, example="2025-03-08T21:20:00Z")
                }
            )
        ),
        404: openapi.Response(
            description="URL not found or not accessible by this user.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="URL not found or not accessible by this user")
                }
            )
        ),
        500: openapi.Response(
            description="An internal error occurred.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="An unexpected error occurred.")
                }
            )
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_url_analytics(request, shortUrl):
    """
    Fetch analytics for a specific shortened URL.
    """
    try:
        url = URL.objects.get(short_code=shortUrl, user=request.user)
        data  = URLSerializer(url).data
        
        return Response({"status": "success", "data": data, "created_at": url.created_at}, status=status.HTTP_200_OK)
    except URL.DoesNotExist:
        return Response({"status": "error", "message": "URL not found or not accessible by this user"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@swagger_auto_schema(
    methods=['GET'],  # Explicitly specify the method to apply the decorator to
    operation_description="Redirect to the original long URL based on the short code.",
    manual_parameters=[
        openapi.Parameter(
            'shortUrl',  # The parameter name in the URL
            openapi.IN_PATH,  # This is a path parameter
            description="The shortened URL code to redirect to the original long URL",
            type=openapi.TYPE_STRING,
            required=True,
            example="abcd1234"
        )
    ],
    responses={
        302: openapi.Response(
            description="Successfully redirected to the original long URL.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Redirected successfully")
                }
            )
        ),
        404: openapi.Response(
            description="Shortened URL not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Shortened URL not found")
                }
            )
        ),
        500: openapi.Response(
            description="An internal error occurred.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="An unexpected error occurred.")
                }
            )
        )
    }
)
@api_view(['GET'])
def redirect_url(request, shortUrl):
    """
    Redirect to the original long URL based on the short code.
    """
    try:
        url = URL.objects.get(short_code=shortUrl)
        url.clicks += 1  # Increment click count on access
        url.save()
        
        return HttpResponseRedirect(url.long_url)
    except URL.DoesNotExist:
        return Response({"status": "error", "message": "Shortened URL not found"}, status=status.HTTP_404_NOT_FOUND)





