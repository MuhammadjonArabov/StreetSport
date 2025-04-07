from django.shortcuts import render
from rest_framework import generics, status
from .serializers import RegisterSerializers, LoginSerializers
from .models import User
from rest_framework.response import Response


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializers

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializers

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        data = {
            "phone_number": user.phone_number,
            "full_name": user.full_name,
            "tokens": user.tokens(),
        }
        return Response(data, status=status.HTTP_200_OK)