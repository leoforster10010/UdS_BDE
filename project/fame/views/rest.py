from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from fame.models import FameUsers, ExpertiseAreas
from fame.serializers import (
    FameUsersSerializer,
    ExpertiseAreasSerializer,
    FameSerializer,
)
from socialnetwork import api
from socialnetwork.api import _get_social_network_user


class ExpertiseAreasApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        posts = ExpertiseAreas.objects.all()
        serializer = ExpertiseAreasSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = {
            "label": request.data.get("label"),
            "parent_expertise_area": request.data.get("parent_expertise_area"),
        }
        serializer = ExpertiseAreasSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FameUsersApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        posts = FameUsers.objects.all()
        serializer = FameUsersSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        raise PermissionError()


class FameListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        user, _fame = api.fame(_get_social_network_user(request.user))
        serializer = FameSerializer(_fame, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        raise NotImplementedError()
