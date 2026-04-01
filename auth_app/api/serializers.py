from rest_framework import serializers
from django.contrib.auth.models import User

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_fullname(self, value):
        """
        Ensure that the provided fullname is not already used
        as a username.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        """
        Ensure that the provided email address is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate(self, attrs):
        """
        Validate that both password fields match before creating
        a new user account.
        """
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """
        Create a new user account and map fullname to username.
        """
        validated_data.pop("repeated_password")
        fullname = validated_data.pop("fullname")
        password = validated_data.pop("password")

        user = User(
            username=fullname,
            email=validated_data["email"]
        )
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Authenticate a user by email and password and attach the
        matching user object to the validated data.
        """
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"error": "Email or password is incorrect."}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"error": "Email or password is incorrect."}
            )

        data["user"] = user
        return data