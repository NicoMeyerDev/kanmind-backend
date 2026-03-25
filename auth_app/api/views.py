from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import RegistrationSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]# Hier allowany weil der nutzer noch nicht auth sein kann

    def post(self, request):
        serializer = RegistrationSerializer(data= request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created  = Token.objects.get_or_create(user=saved_account)
            data = {
            "token": token.key,
            "username": saved_account.username,
            "email": saved_account.email
        }
        else:
            data = serializer.errors
        return Response(data)

class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]# Hier allowany weil der nutzer noch nicht auth sein kann

    def post(self, request):
        serializer = self.serializer_class(data= request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created  = Token.objects.get_or_create(user=user)
            #Hier Möglichkeit der personalisierung um mehr oder weniger infos zurückzugeben
            data = {
            "token": token.key,
            "username": user.username,
            "email": user.email
        }
        else:
            data = serializer.errors
        return Response(data)