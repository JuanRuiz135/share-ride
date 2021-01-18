""" Users views. """

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Serializers
from cride.users.serializers import UserLoginSerializer

class UserLoginAPIView():
    """ User login API view. """

    def post(self, request, *args, **kwargs):
        """ Handle HTTP POST request. """
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        data = {
            'status': 'ok',
            'token': token
        }
        return Response(data, status=status.HTTP_201_CREATED)