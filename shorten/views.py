from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import URL
from .serializers import URLSerializer

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

from django.http import HttpResponseRedirect

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





