from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import URL, ClickEvent
from .serializers import URLSerializer
from django.http import HttpResponseRedirect
from django.utils import timezone
from url_shortener import settings
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.db.models import Count
import requests


@swagger_auto_schema(
    method="post",
    operation_description="Shorten a given URL for the authenticated user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "long_url": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The URL to be shortened",
                example="https://www.example.com",
            )
        },
        required=["long_url"],
    ),
    responses={
        201: openapi.Response(description="URL was successfully created.", schema=URLSerializer),
        400: openapi.Response(
            description="Long URL is required.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, example="Long URL is required"),
                },
            ),
        ),
        500: openapi.Response(
            description="An internal error occurred.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="An unexpected error occurred.",
                    ),
                },
            ),
        ),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def shorten_url(request):
    """
    Shorten a given URL for the authenticated user.
    """
    try:
        serializer = URLSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Invalid input",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a new URL record
        url = serializer.save(user=request.user)
        return Response(
            {
                "status": "success",
                "message": "Url record was created",
                "data": URLSerializer(url).data,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    methods=["GET"],  # Explicitly specify the method to apply the decorator to
    operation_description="Fetch all shortened URLs for the authenticated user.",
    responses={
        200: openapi.Response(
            description="URLs were successfully retrieved.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Urls were successfully retrieved",
                    ),
                    "data": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "long_url": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="https://www.example.com",
                                ),
                                "shortened_url": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="https://short.ly/abcd1234",
                                ),
                            },
                        ),
                        description="List of shortened URLs for the authenticated user",
                    ),
                },
            ),
        ),
        500: openapi.Response(
            description="An internal error occurred.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="An unexpected error occurred.",
                    ),
                },
            ),
        ),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_urls(request):
    """
    Fetch all shortened URLs for the authenticated user.
    """
    try:
        urls = URL.objects.filter(user=request.user)
        serializer = URLSerializer(urls, many=True)
        return Response(
            {
                "status": "success",
                "message": "Urls were successfully retrieved",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    methods=["DELETE"],
    operation_description="Delete a shortened URL for the authenticated user.",
    responses={
        200: openapi.Response(
            description="URL was successfully deleted.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Your url has been deleted successful",
                    ),
                    "data": openapi.Schema(type=openapi.TYPE_OBJECT, example={}),
                },
            ),
        ),
        404: openapi.Response(
            description="URL not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, example="URL not found."),
                },
            ),
        ),
        500: openapi.Response(
            description="An internal error occurred.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="An unexpected error occurred.",
                    ),
                },
            ),
        ),
    },
)
@api_view(["DELETE"])
def delete_url(request, url_id):
    """
    Fetch all shortened URLs for the authenticated user.
    """
    try:
        url = URL.objects.get(user=request.user, pk=url_id)
        url.delete()
        return Response(
            {
                "status": "success",
                "message": "Your url has been deleted successful",
                "data": {},
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    methods=["GET"],
    operation_description="Fetch analytics for a specific shortened URL.",
    manual_parameters=[
        openapi.Parameter(
            "shortUrl",
            openapi.IN_PATH,
            description="The shortened URL code to fetch analytics for",
            type=openapi.TYPE_STRING,
            required=True,
            example="abcd1234",
        )
    ],
    responses={
        200: openapi.Response(
            description="Analytics for the shortened URL were successfully retrieved.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "short_code": openapi.Schema(type=openapi.TYPE_STRING, example="abcd1234"),
                            "long_url": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="https://www.example.com",
                            ),
                            "shortened_url": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="https://short.ly/abcd1234",
                            ),
                            "total_clicks": openapi.Schema(type=openapi.TYPE_INTEGER, example=150),
                            "click_distribution": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "daily": openapi.Schema(type=openapi.TYPE_OBJECT),
                                    "weekly": openapi.Schema(type=openapi.TYPE_OBJECT),
                                    "monthly": openapi.Schema(type=openapi.TYPE_OBJECT),
                                },
                            ),
                        },
                    ),
                    "created_at": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATETIME,
                        example="2025-03-08T21:20:00Z",
                    ),
                },
            ),
        ),
        404: openapi.Response(
            description="URL not found or not accessible by this user.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="URL not found or not accessible by this user",
                    ),
                },
            ),
        ),
        500: openapi.Response(
            description="An internal error occurred.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="An unexpected error occurred.",
                    ),
                },
            ),
        ),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_url_analytics(request, shortUrl):
    """
    Fetch analytics for a specific shortened URL, including click distribution over time.
    """
    try:
        url = URL.objects.get(short_code=shortUrl, user=request.user)

        # Get all click events for this URL
        click_events = ClickEvent.objects.filter(url=url).order_by("-clicked_at")

        # Aggregate clicks grouped by different time periods
        daily_clicks = click_events.annotate(day=TruncDay("clicked_at")).values("day").annotate(count=Count("id"))

        weekly_clicks = click_events.annotate(week=TruncWeek("clicked_at")).values("week").annotate(count=Count("id"))

        monthly_clicks = click_events.annotate(month=TruncMonth("clicked_at")).values("month").annotate(count=Count("id"))

        # Get location-based analytics
        country_stats = click_events.exclude(country__isnull=True).values("country").annotate(count=Count("id")).order_by("-count")

        city_stats = click_events.exclude(city__isnull=True).values("city").annotate(count=Count("id")).order_by("-count")

        # Get referrer statistics
        referrer_stats = click_events.exclude(referrer__isnull=True).values("referrer").annotate(count=Count("id")).order_by("-count")

        # Get recent clicks with detailed information
        recent_clicks = click_events[:10].values(
            "clicked_at",
            "ip_address",
            "country",
            "city",
            "region",
            "user_agent",
            "referrer",
        )

        # Convert queryset results to dictionary format
        click_distribution = {
            "daily": {entry["day"].strftime("%Y-%m-%d"): entry["count"] for entry in daily_clicks},
            "weekly": {entry["week"].strftime("%Y-%U"): entry["count"] for entry in weekly_clicks},
            "monthly": {entry["month"].strftime("%Y-%m"): entry["count"] for entry in monthly_clicks},
        }

        # Serialize and return the data
        data = {
            "short_code": url.short_code,
            "long_url": url.long_url,
            "created_at": url.created_at,
            "total_clicks": url.clicks,
            "click_distribution": click_distribution,
            "location_analytics": {
                "countries": list(country_stats),
                "cities": list(city_stats),
            },
            "referrer_analytics": list(referrer_stats),
            "recent_clicks": list(recent_clicks),
        }

        return Response(
            {"status": "success", "data": data, "created_at": url.created_at},
            status=status.HTTP_200_OK,
        )

    except URL.DoesNotExist:
        return Response(
            {
                "status": "error",
                "message": "URL not found or not accessible by this user",
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    methods=["GET"],  # Explicitly specify the method to apply the decorator to
    operation_description="Redirect to the original long URL based on the short code.",
    manual_parameters=[
        openapi.Parameter(
            "shortUrl",  # The parameter name in the URL
            openapi.IN_PATH,  # This is a path parameter
            description="The shortened URL code to redirect to the original long URL",
            type=openapi.TYPE_STRING,
            required=True,
            example="abcd1234",
        )
    ],
    responses={
        302: openapi.Response(
            description="Successfully redirected to the original long URL.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, example="Redirected successfully"),
                },
            ),
        ),
        404: openapi.Response(
            description="Shortened URL not found.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, example="Shortened URL not found"),
                },
            ),
        ),
        500: openapi.Response(
            description="An internal error occurred.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="An unexpected error occurred.",
                    ),
                },
            ),
        ),
    },
)
@api_view(["GET"])
def redirect_url(request, shortUrl):
    """
    Redirect to the original long URL based on the short code.
    """
    try:
        url = URL.objects.get(short_code=shortUrl)

        # Get IP address
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        # Get geolocation data
        geo_data = get_ip_geolocation(ip)

        # Create click event with all the information
        ClickEvent.objects.create(
            url=url,
            ip_address=ip,
            country=geo_data["country"],
            city=geo_data["city"],
            region=geo_data["region"],
            user_agent=request.META.get("HTTP_USER_AGENT"),
            referrer=request.META.get("HTTP_REFERER"),
        )

        url.clicks += 1  # Increment click count on access
        url.clicked_date = timezone.now()
        url.save()

        return HttpResponseRedirect(url.long_url)
    except URL.DoesNotExist:
        return Response(
            {"status": "error", "message": "Shortened URL not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


def get_ip_geolocation(ip):
    """
    Get geolocation data for an IP address using ipapi.co
    """
    try:
        response = requests.get(f"{settings.GEOLOCATION_BASE_URL}/{ip}/json/")
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country_name"),
                "city": data.get("city"),
                "region": data.get("region"),
            }
    except Exception:
        pass
    return {"country": None, "city": None, "region": None}
