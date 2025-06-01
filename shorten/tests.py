from django.test import TestCase
from users.models import CustomUser as User
from .models import URL, ClickEvent, generate_short_code
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
import json


class URLModelTest(TestCase):
    def setUp(self):
        # Create a sample user for testing
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )

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

    def test_url_clicks_tracking(self):
        """
        Test that URL clicks are properly tracked.
        """
        url = URL.objects.create(
            user=self.user,
            long_url="https://www.example.com",
            name="test"
        )
        
        # Initial clicks should be 0
        self.assertEqual(url.clicks, 0)
        
        # Increment clicks
        url.clicks += 1
        url.clicked_date = timezone.now()
        url.save()
        
        # Check if clicks were updated
        url.refresh_from_db()
        self.assertEqual(url.clicks, 1)
        self.assertIsNotNone(url.clicked_date)


class ClickEventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )
        self.url = URL.objects.create(
            user=self.user,
            long_url="https://www.example.com",
            name="test"
        )

    def test_create_click_event(self):
        """
        Test creating a click event with all fields.
        """
        click_event = ClickEvent.objects.create(
            url=self.url,
            ip_address="192.168.1.1",
            country="US",
            city="New York",
            region="NY",
            user_agent="Mozilla/5.0",
            referrer="https://google.com"
        )

        self.assertEqual(click_event.url, self.url)
        self.assertEqual(click_event.ip_address, "192.168.1.1")
        self.assertEqual(click_event.country, "US")
        self.assertEqual(click_event.city, "New York")
        self.assertEqual(click_event.region, "NY")
        self.assertEqual(click_event.user_agent, "Mozilla/5.0")
        self.assertEqual(click_event.referrer, "https://google.com")
        self.assertIsNotNone(click_event.clicked_at)


class URLAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )
        
        # Create a test URL
        self.url = URL.objects.create(
            user=self.user,
            long_url="https://www.example.com",
            name="test"
        )
        
        # Login the user
        self.client.force_authenticate(user=self.user)

    def test_shorten_url(self):
        """
        Test the URL shortening endpoint.
        """
        data = {
            "long_url": "https://www.new-example.com",
            "name": "new test"
        }
        response = self.client.post(reverse('shorten'), data, format='json')
        
        if response.status_code != status.HTTP_201_CREATED:
            print('Response data:', response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['long_url'], data['long_url'])

    def test_get_user_urls(self):
        """
        Test retrieving all URLs for the authenticated user.
        """
        # Create another URL for the same user
        URL.objects.create(
            user=self.user,
            long_url="https://www.another-example.com",
            name="another test"
        )
        
        # Get all URLs for the user
        response = self.client.get(reverse('urls'))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 2)  # Should have 2 URLs