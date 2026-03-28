from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import RegistrationSerializer, LoginSerializer  

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
            "fullname": saved_account.username,
            "email": saved_account.email,
            "user_id": saved_account.id
        }
            return Response(data, status=201)
        else:
            data= serializer.errors
            return Response(data, status=400)
    

class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer  

    def post(self, request):
        serializer = self.serializer_class(data=request.data)  
        data = {}
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            data = {
                "token": token.key,
                "fullname": user.username,
                "email": user.email,
                "user_id": user.id
            }
            return Response(data, status=200) 
        else:
            data = serializer.errors
            return Response(data, status=400)
    
class LogoutView(APIView):

    def post(self, request):
        request.user.auth_token.delete()  # Token löschen
        return Response({"detail": "Logout erfolgreich. Token wurde gelöscht."}, status=status.HTTP_200_OK)    