from rest_framework import serializers
from .models import URL
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import re


class URLSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate_long_url(self, value):
        # Remove any whitespace
        value = value.strip()

        # Check if URL starts with http:// or https://
        if not re.match(r"^https?://", value):
            value = "https://" + value

        # Validate URL format
        validator = URLValidator()
        try:
            validator(value)
        except ValidationError:
            raise serializers.ValidationError("Please enter a valid URL")

        # Additional security checks
        # Block common malicious patterns
        malicious_patterns = [
            r"javascript:",  # JavaScript protocol
            r"data:",  # Data URLs
            r"vbscript:",  # VBScript protocol
            r"file:",  # File protocol
            r"about:",  # About protocol
            r"blob:",  # Blob URLs
            r"ftp:",  # FTP protocol
        ]

        for pattern in malicious_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise serializers.ValidationError("This URL scheme is not allowed")

        return value

    class Meta:
        model = URL
        fields = "__all__"
