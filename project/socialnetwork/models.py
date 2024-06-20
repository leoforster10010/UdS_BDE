import random as rnd

from django.contrib.auth.models import AbstractUser
from django.db import models

from fame.models import ExpertiseAreas, FameUsers
from socialnetwork.magic_AI import classify_into_expertise_areas_and_check_for_bullshit

rnd.seed(42)


class SocialNetworkUsers(FameUsers):
    """Users of the social network."""

    follows = models.ManyToManyField(
        "self", symmetrical=False, related_name="followed_by"
    )
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        db_table = "social_network_users"


class Posts(models.Model):
    """Posts in the social network."""

    content = models.CharField(max_length=42 * 42, null=False)
    author = models.ForeignKey("SocialNetworkUsers", on_delete=models.CASCADE)
    submitted = models.DateTimeField(auto_now_add=True)

    cites = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="cited_by"
    )
    replies_to = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replied_to",
    )

    expertise_area_and_truth_ratings = models.ManyToManyField(
        ExpertiseAreas,
        symmetrical=False,
        related_name="classified_as",
        through="PostExpertiseAreasAndRatings",
    )
    user_ratings = models.ManyToManyField(
        SocialNetworkUsers,
        symmetrical=False,
        related_name="rated_by",
        through="UserRatings",
    )

    published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-submitted"]
        unique_together = ("author", "submitted")
        db_table = "posts"

    def determine_expertise_areas_and_truth_ratings(self):
        # ask the mighty AI to classify_into_expertise_areas the content into expertise areas:
        _expertise_areas = classify_into_expertise_areas_and_check_for_bullshit(
            self.content
        )

        # create the expertise areas and truth ratings:
        at_least_one_expertise_area_contains_bullshit = False

        for epa in _expertise_areas:
            PostExpertiseAreasAndRatings.objects.create(
                post=self,
                expertise_area=epa["expertise_area"],
                truth_rating=epa["truth_rating"],
            )
            if epa["truth_rating"] and epa["truth_rating"].numeric_value < 0:
                at_least_one_expertise_area_contains_bullshit = True

        return at_least_one_expertise_area_contains_bullshit, _expertise_areas

    def __str__(self):
        return f"{self.author} - {self.submitted} - {self.content[:10]}..."


class TruthRatings(models.Model):
    """Ratings of the truthfulness of a post. Not to be confused with ExpertiseAreas!"""

    name = models.CharField(max_length=42)
    numeric_value = models.IntegerField(null=False)

    def __str__(self):
        return f"{self.name} ({self.numeric_value})"

    class Meta:
        db_table = "truth_ratings"


class PostExpertiseAreasAndRatings(models.Model):
    """Expertise areas and truth ratings determined for the contents of a post."""

    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    expertise_area = models.ForeignKey(ExpertiseAreas, on_delete=models.CASCADE)
    truth_rating = models.ForeignKey(TruthRatings, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ("post", "expertise_area")

    def __str__(self):
        return f"{self.post} - {self.expertise_area} - {self.truth_rating}"

    class Meta:
        db_table = "post_expertise_areas_and_ratings"


class UserRatings(models.Model):
    """User ratings and/or approvals of a post."""

    APPROVAL = "A"
    LIKE = "L"
    DISLIKE = "D"
    RATING_TYPES = [(APPROVAL, "Approval"), (LIKE, "Like"), (DISLIKE, "Dislike")]

    user = models.ForeignKey(SocialNetworkUsers, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    score = models.IntegerField()
    type = models.CharField(
        max_length=1,
        choices=RATING_TYPES,
        default=LIKE,
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post", "type")

    def __str__(self):
        return f"{self.user} - {self.post} - {self.type} - {self.score}"
