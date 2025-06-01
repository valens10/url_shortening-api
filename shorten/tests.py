from django.test import TestCase
from users.models import CustomUser as User
from .models import URL, generate_short_code


class URLModelTest(TestCase):
    def setUp(self):
        # Create a sample user for testing
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password123")

    def test_create_url_with_short_code(self):
        """
        Test that a URL object is created with a valid short code.
        """
        long_url = "https://www.example.com"
        name = "test"
        url = URL.objects.create(user=self.user, long_url=long_url, name=name)

        # Check if short_code is generated and is not blank
        self.assertIsNotNone(url.short_code)
        self.assertTrue(len(url.short_code) > 0)
        self.assertNotEqual(url.short_code, "")

    def test_short_code_uniqueness(self):
        """
        Test that the short code is unique.
        """
        long_url_1 = "https://www.example.com"
        long_url_2 = "https://www.anotherexample.com"
        name = "test"

        # Create two URL objects for the same user
        url1 = URL.objects.create(user=self.user, long_url=long_url_1, name=name)
        url2 = URL.objects.create(user=self.user, long_url=long_url_2, name=name)

        # Ensure that both URLs have different short codes
        self.assertNotEqual(url1.short_code, url2.short_code)

    def test_url_association_with_user(self):
        """
        Test that a URL object is correctly associated with the user.
        """
        long_url = "https://www.example.com"
        name = "test"
        url = URL.objects.create(user=self.user, long_url=long_url, name=name)

        # Check if the URL's user is correctly associated
        self.assertEqual(url.user, self.user)

    def test_generate_short_code_function(self):
        """
        Test the `generate_short_code` function to ensure it generates a unique code.
        """
        # Generate a short code and check if it exists
        code = generate_short_code()

        # Ensure the generated short code is unique
        self.assertIsNotNone(code)
        self.assertTrue(len(code) == 12)  # Check that it's 12 characters long
        self.assertTrue(code.isalnum())  # Check that it's alphanumeric

        # Ensure that the generated short code does not already exist
        self.assertFalse(URL.objects.filter(short_code=code).exists())
