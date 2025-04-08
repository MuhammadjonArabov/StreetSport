from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import RegisterSerializers, LoginSerializers, LogoutSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
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

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT)

class CustomTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required"}, status=400)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            return Response({"access": new_access_token})
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class ChangePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        data = request.data

        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not old_password or not new_password:
            return Response({"detail": "Old and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            raise AuthenticationFailed("Old password is incorrect.")

        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)
