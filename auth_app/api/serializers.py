from rest_framework import serializers
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):

    repeated_password = serializers.CharField(write_only = True)
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs ={
            "password":{
                "write_only": True
            }
        }

    def create(self, validated_data):
        pw= self.validated_data["password"]
        repeated_password = self.validated_data["repeated_password"]

        if pw != repeated_password:
            raise serializers.ValidationError({"error": "password stimmen nicht überein!"})

        account = User(
            email=self.validated_data["email"],
            username=self.validated_data["fullname"]  
        )
        account.set_password(pw)
        account.save()
        return account   
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "Email oder Passwort falsch"})

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "Email oder Passwort falsch"})

        data["user"] = user
        return data    