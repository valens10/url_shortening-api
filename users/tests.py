from django.test import TestCase
from users.models import CustomUser  # Adjust import based on your app structure
import uuid
from django.core.exceptions import ValidationError

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model


class CustomUserModelTest(TestCase):
    def setUp(self):
        """
        Create a sample user for testing.
        """
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )

    def test_create_user_with_valid_data(self):
        """
        Test that a user is created with valid data.
        """
        self.assertIsInstance(self.user, CustomUser)
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertTrue(self.user.check_password("password123"))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_user_uuid_as_primary_key(self):
        """
        Test that the user ID is a UUID.
        """
        self.assertIsInstance(self.user.id, uuid.UUID)

    def test_user_unique_email(self):
        """
        Test that the email field is unique.
        """
        with self.assertRaises(Exception):  # Check if creating a duplicate email raises an exception
            CustomUser.objects.create_user(
                username="anotheruser",
                email="testuser@example.com",
                first_name="Jane",
                last_name="Doe",
                password="password123",
            )

    def test_user_unique_username(self):
        """
        Test that the username field is unique.
        """
        with self.assertRaises(Exception):  # Check if creating a duplicate username raises an exception
            CustomUser.objects.create_user(
                username="testuser",
                email="anotheruser@example.com",
                first_name="Jane",
                last_name="Doe",
                password="password123",
            )

    def test_user_gender_choices(self):
        """
        Test that the gender field can only take predefined values.
        """
        user_male = CustomUser.objects.create_user(
            username="maleuser",
            email="maleuser@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
            gender="MALE",
        )
        user_female = CustomUser.objects.create_user(
            username="femaleuser",
            email="femaleuser@example.com",
            first_name="Jane",
            last_name="Doe",
            password="password123",
            gender="FEMALE",
        )
        self.assertEqual(user_male.gender, "MALE")
        self.assertEqual(user_female.gender, "FEMALE")

        # Create a user with an invalid gender to trigger validation error
        invalid_user = CustomUser(
            username="invaliduser",
            email="invaliduser@example.com",
            first_name="Invalid",
            last_name="User",
            password="password123",
            gender="OTHER",  # Invalid gender
        )

        # The following line manually triggers model validation
        with self.assertRaises(ValidationError):
            invalid_user.full_clean()  # This will call the clean method


class UserLoginTest(APITestCase):

    def setUp(self):
        """
        Create a user for testing login functionality.
        """
        self.username = "testuser"
        self.password = "password123"
        self.user = get_user_model().objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
        )
        # Create a valid payload for login
        self.login_data = {"username": self.username, "password": self.password}

    def test_login_success(self):
        """
        Test a successful login with valid credentials.
        """
        response = self.client.post("/auth/login", self.login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertIn("token", response.data["data"])

    def test_login_invalid_credentials(self):
        """
        Test login with invalid credentials (wrong password).
        """
        invalid_data = {"username": self.username, "password": "wrongpassword"}
        response = self.client.post("/auth/login", invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(response.data["message"], "Invalid credentials.")

    def test_login_missing_fields(self):
        """
        Test login with missing fields (either username or password).
        """
        # Missing password
        invalid_data = {"username": self.username}
        response = self.client.post("/auth/login", invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(response.data["message"], "Username and password are required.")

        # Missing username
        invalid_data = {"password": self.password}
        response = self.client.post("/auth/login", invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(response.data["message"], "Username and password are required.")

    def test_login_inactive_user(self):
        """
        Test login with an inactive user.
        """
        # Deactivate the user
        self.user.is_active = False
        self.user.save()

        response = self.client.post("/auth/login", self.login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(response.data["message"], "Invalid username or inactive account.")
