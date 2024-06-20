from django.db.models import Sum
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Posts, SocialNetworkUsers


class SocialNetworkUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialNetworkUsers
        fields = "__all__"


class PostsSerializer(serializers.ModelSerializer):
    expertise_area_and_truth_ratings = SerializerMethodField()
    date_submitted = SerializerMethodField()
    user_ratings = SerializerMethodField()
    author = SerializerMethodField()
    citations = SerializerMethodField()
    replies = SerializerMethodField()

    class Meta:
        model = Posts
        fields = [
            "content",
            "author",
            "expertise_area_and_truth_ratings",
            "date_submitted",
            "user_ratings",
            "citations",
            "replies",
            "published",
        ]

    def get_expertise_area_and_truth_ratings(self, post: Posts):
        ret = {}
        for pear in post.postexpertiseareasandratings_set.all():
            if pear.truth_rating is None:
                ret[pear.expertise_area.label] = {
                    "name": "unknown",
                    "numeric_value": 0,
                }
            else:
                ret[pear.expertise_area.label] = {
                    "name": pear.truth_rating.name,
                    "numeric_value": pear.truth_rating.numeric_value,
                }
        return ret

    def get_citations(self, post: Posts):
        return Posts.objects.filter(cites=post).count()

    def get_replies(self, post: Posts):
        return Posts.objects.filter(replies_to=post).count()

    def get_date_submitted(self, post: Posts):
        return post.submitted.strftime("%Y-%m-%d %H:%M")

    def get_user_ratings(self, post: Posts):
        ret = {}
        for pur in post.userratings_set.values("type").annotate(score=Sum("score")):
            ret[pur["type"]] = pur["score"]
        return ret

    def get_author(self, post: Posts):
        return {
            "id": post.author.id,
            "email": post.author.email,
            "name": post.author.first_name + " " + post.author.last_name,
        }
