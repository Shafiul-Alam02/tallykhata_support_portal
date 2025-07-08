from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError
from .models import user_profile  # Assuming your profile model is in the same app


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Check the user's department in the user_profile model
        try:
            profile = user_profile.objects.get(user=user)
            if profile.department != "TECHOPS":
                raise TokenError("You do not have permission to obtain a token.")
        except user_profile.DoesNotExist:
            raise TokenError("User profile not found.")

        return data
