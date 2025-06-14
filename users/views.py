from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from .models import CustomUser as User


class UserRegisterViewset(GenericAPIView, CreateModelMixin):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(
        operation_description="Register a new user.",
        request_body=UserSerializer,
        responses={
            201: openapi.Response(description="User registered successfully!", schema=UserSerializer),
            400: openapi.Response(
                description="User registration failed.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="User registration failed. Please correct the errors and try again.",
                        ),
                        "errors": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additionalProperties=openapi.TYPE_STRING,
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():

            error_message = ""
            for field, messages in serializer.errors.items():
                error_message += f'{", ".join(messages)} '
            return Response(
                {
                    "status": "error",
                    "message": error_message,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.validated_data["is_active"] = True
        self.perform_create(serializer)
        return Response(
            {
                "status": "success",
                "message": "Your account has been registered successfully!",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class UserDetailViewset(GenericAPIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    @swagger_auto_schema(
        operation_description="Retrieve details of the authenticated user.",
        responses={
            200: openapi.Response(
                description="User details retrieved successfully.",
                schema=UserSerializer(),
            ),
            401: openapi.Response(description="Authentication credentials were not provided."),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update details of the authenticated user (partial update).",
        request_body=UserSerializer,
        responses={
            200: openapi.Response(
                description="User details updated successfully.",
                schema=UserSerializer(),
            ),
            400: openapi.Response(description="Invalid data provided."),
            401: openapi.Response(description="Authentication required."),
        },
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete the authenticated user.",
        responses={
            204: openapi.Response(description="User deleted successfully."),
            401: openapi.Response(description="Authentication required."),
        },
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"detail": "User deleted successfully."}, status=204)


@swagger_auto_schema(
    method="post",
    operation_description="Authenticate a user with username and password.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["username", "password"],
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="User's password",
                format="password",
            ),
        },
    ),
    responses={
        200: openapi.Response(
            description="Authentication successful.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, example="Authentication successful."),
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                            "username": openapi.Schema(type=openapi.TYPE_STRING, example="johndoe"),
                            "email": openapi.Schema(type=openapi.TYPE_STRING, example="johndoe@example.com"),
                            "token": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            ),
                            "token_refresh": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            ),
                        },
                    ),
                },
            ),
        ),
        400: openapi.Response(
            description="Invalid username, inactive account, or invalid credentials.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, example="Invalid credentials."),
                },
            ),
        ),
    },
)
@api_view(["POST"])
def login(request):
    """
    Authenticate a user with username and password.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    print(username, password)

    if not username or not password:
        return Response(
            {"status": "error", "message": "Username and password are required."},
            status=400,
        )

    try:
        user = User.objects.filter(username=username, is_active=True).first()
        if not user:
            return Response(
                {"status": "error", "message": "Invalid username or inactive account."},
                status=400,
            )

        user = authenticate(username=username, password=password, request=request)
        if not user:
            return Response({"status": "error", "message": "Invalid credentials."}, status=400)

        # Serialize user data
        data = UserSerializer(user).data

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        data["token"] = str(refresh.access_token)
        data["token_refresh"] = str(refresh)

        return Response(
            {"status": "success", "message": "Login successful.", "data": data},
            status=200,
        )

    except Exception as e:
        return Response({"status": "error", "message": "An error occurred: " + str(e)}, status=500)


@swagger_auto_schema(
    method="post",
    operation_description="Logout the authenticated user by blacklisting their refresh token.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "refresh_token": openapi.Schema(type=openapi.TYPE_STRING, description="The refresh token to blacklist"),
        },
    ),
    responses={
        200: openapi.Response(description="Successfully logged out."),
        400: openapi.Response(description="Invalid refresh token."),
        401: openapi.Response(description="Authentication required."),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout an authenticated user by blacklisting their refresh token"""
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token is required"}, status=400)

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"detail": "Successfully logged out"}, status=200)
    except Exception as e:
        return Response({"detail": str(e)}, status=400)


@swagger_auto_schema(
    method="get",
    operation_description="Fetch the authenticated user's data.",
    responses={
        200: openapi.Response(description="Data successfully fetched."),
        401: openapi.Response(description="You are not allowed to perform this operation."),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    """
    Retrieve authenticated user data.

    Returns the details of the currently authenticated user.

    **Permissions:**
    - Requires authentication
    """
    try:
        user = request.user
        user_data = UserSerializer(user).data

        # regenerate JWT tokens
        refresh = RefreshToken.for_user(user)
        user_data["token"] = str(refresh.access_token)
        user_data["token_refresh"] = str(refresh)

        return Response(
            {
                "status": "success",
                "message": "Data successfully fetched.",
                "data": user_data,
            },
            status=200,
        )
    except Exception as e:
        return Response({"status": "error", "message": "An error occurred: " + str(e)}, status=500)
