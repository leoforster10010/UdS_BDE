from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from socialnetwork import api
from socialnetwork.api import timeline, _get_social_network_user
from socialnetwork.serializers import PostsSerializer


class PostsListApiView(APIView):
    # check permission if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all social network posts through a GET call
    def get(self, request, *args, **kwargs):
        """
        List all posts items
        """
        posts = timeline(_get_social_network_user(request.user))
        serializer = PostsSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create a post in the social network through a POST call
    def post(self, request, *args, **kwargs):
        ret, _expertise_areas, redirect_to_logout = api.submit_post(
            user=_get_social_network_user(request.user),
            content=request.data.get("text"),
        )
        if redirect_to_logout:
            logout(request)
            assert request.user.is_authenticated is False
            return redirect(reverse("login"))

        assert request.user.is_authenticated is True
        return redirect(reverse("sn:timeline"))
