from django.shortcuts import render
from rest_framework import generics
from .serializers import RegisterSerializers


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializers
