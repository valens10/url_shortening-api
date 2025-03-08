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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": "error", "message": "User registration failed. Please correct the errors and try again.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


        self.perform_create(serializer)
        return Response({"status": "success", "message": "User registered successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)


class UserDetailViewset(GenericAPIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"detail": "User deleted successfully."}, status=204)
    
    
    
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


    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout(request):
        if request.user.is_anonymous:
            return Response({"detail": "You are not allowed to perform this operation"}, status=401)
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": "Signed out"}, status=200)
