from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import UserSerializer
from .models import CustomUser as User

class UserRegisterViewset(GenericAPIView, CreateModelMixin):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(
        operation_description="Register a new user.",
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully!",
                schema=UserSerializer
            ),
            400: openapi.Response(
                description="User registration failed.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="User registration failed. Please correct the errors and try again."),
                        'errors': openapi.Schema(type=openapi.TYPE_OBJECT, additionalProperties=openapi.TYPE_STRING),
                    }
                )
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "message": "Account registration failed. Please correct the errors and try again.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        return Response(
            {"status": "success", "message": "Your account has been registered successfully!", "data": serializer.data},
            status=status.HTTP_201_CREATED
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
                schema=UserSerializer()
            ),
            401: openapi.Response(description="Authentication credentials were not provided."),
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update details of the authenticated user (partial update).",
        request_body=UserSerializer,
        responses={
            200: openapi.Response(
                description="User details updated successfully.",
                schema=UserSerializer()
            ),
            400: openapi.Response(description="Invalid data provided."),
            401: openapi.Response(description="Authentication required."),
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete the authenticated user.",
        responses={
            204: openapi.Response(description="User deleted successfully."),
            401: openapi.Response(description="Authentication required."),
        }
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"detail": "User deleted successfully."}, status=204)
    


@swagger_auto_schema(
    method='post',
    operation_description="Authenticate a user with username and password.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="User's password", format="password"),
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
                            "token": openapi.Schema(type=openapi.TYPE_STRING, example="abcd1234xyz"),
                        }
                    ),
                }
            ),
        ),
        400: openapi.Response(
            description="Invalid username, inactive account, or invalid credentials.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Invalid credentials."),
                }
            )
        ),
    }
)
@api_view(['POST'])
def login(request):
    """
    Authenticate a user with username and password.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({
            "status": "error",
            "message": "Username and password are required."
        }, status=400)

    try:
        user = User.objects.filter(username=username, is_active=True).first()
        if not user:
            return Response({"status": "error", "message": "Invalid username or inactive account."}, status=400)

        user = authenticate(username=username, password=password, request=request)
        if not user:
            return Response({"status": "error", "message": "Invalid credentials."}, status=400)

        # Serialize user data
        data = UserSerializer(user).data

        # Get or create token
        token, _ = Token.objects.get_or_create(user=user)
        data["token"] = token.key

        return Response({"status": "success", "message": "Authentication successful.", "data": data}, status=200)

    except Exception as e:
        return Response({"status": "error", "message": "An error occurred: " + str(e)}, status=500)



    
@swagger_auto_schema(
    method='get',
    operation_description="Logout the authenticated user by deleting their token.",
    responses={
        200: openapi.Response(description="Signed out successfully."),
        401: openapi.Response(description="You are not allowed to perform this operation."),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout(request):
    """ Logout an authenticated user and delete their token """
    if request.user.is_anonymous:
        return Response({"detail": "You are not allowed to perform this operation"}, status=401)

    Token.objects.filter(user=request.user).delete()
    return Response({"detail": "Signed out"}, status=200)


@swagger_auto_schema(
    method='get',
    operation_description="Refresh the user's token.",
    responses={
        200: openapi.Response(
            description="Token refreshed successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'token': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                }
            )
        ),
        401: 'Unauthorized',
    }
)
@api_view(['GET'])
def refresh_token(request):
    """
    Refresh the token for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    
    # Get the current user from the request
    user = request.user

    # Serialize user data
    data = UserSerializer(user).data

    # Get or create token
    token, _ = Token.objects.get_or_create(user=user)
    data["token"] = token.key

    # Respond with the new token
    return Response({
        "status": "success",
        "message": "Token refreshed successfully.",
        'data': data
    }, status=status.HTTP_200_OK)
